%global arch %(test $(rpm -E%?_arch) = x86_64 && echo "amd64" || echo "386")
%global debug_package %{nil}
%global project lantern
%global repo %{project}

# commit
%global _commit fdff338235569a69d2120717247439ecc7f774c3
%global _shortcommit %(c=%{_commit}; echo ${c:0:7})
# git show -s --format=%ci "%%{_shortcommit}"
%global _revision_date 2016-01-29 12:04:37 -0800
%global _build_date %(date -u '+%Y%m%d.%H%M%%S')
%global go_arch %(go env GOHOSTARCH)
%global go_root %(go env GOROOT)

%global systemd_user_post() \
if [ $1 -eq 1 ] ; then\
    # Initial installation\
    systemctl preset --user --global %* >/dev/null 2>&1 || :\
fi\
%{nil}

# headless mode: it doesn't depend on the systray support libraries,
# and will not show systray or UI.
%global with_headless 0

# Lantern needs to be compiled twice. Because it requires source code
# in the /usr/share/gocode/src/ directory.
%global with_build 1

Name:    golang-github-getlantern-lantern
Version: 2.0.11
Release: 2.git%{_shortcommit}%{?dist}
Summary: fast, reliable and secure access to the open Internet
Summary(zh_CN): 快速, 可靠, 安全的访问互联网的代理软件

Group:   Applications/Internet
License: Apache 2.0
URL:     https://getlantern.org
Source0: https://github.com/getlantern/lantern/archive/%{_commit}/%{repo}-%{_shortcommit}.tar.gz

Provides: %{repo} = %{version}-%{release}
Obsoletes: %{repo} <= 2.0.11-1.gitfdff338
BuildRequires: systemd
BuildRequires: golang-bin
BuildRequires: gtk3-devel
BuildRequires: libappindicator-gtk3-devel
%if 0%{?with_build}
BuildRequires: golang-github-hashicorp-golang-lru-devel
BuildRequires: golang-github-skratchdot-open-golang-devel
BuildRequires: golang-github-davecgh-go-spew-devel
BuildRequires: golang-bitbucket-kardianos-osext-devel
BuildRequires: golang-googlecode-uuid-devel
BuildRequires: golang-github-gorilla-websocket-devel
BuildRequires: golang-gopkg-check-devel
BuildRequires: %{name}-devel
%endif
Requires: %{name}-ui-devel = %{version}-%{release}
%{systemd_requires}

%description
Lantern is a free desktop application that delivers fast,
reliable and secure access to the open Internet.

Proxy: tcp://127.0.0.1:8787
WebUI: http://127.0.0.1:16823

%description -l zh_CN
Lantern 是一个免费的代理程序, 可以快速、可靠、安全地访问互联网.
它采用多种技术来保持畅通, 包括 P2P 和 domain fronting.

Proxy: tcp://127.0.0.1:8787
WebUI: http://127.0.0.1:16823

%package devel
Requires: %{name}-ui-devel = %{version}-%{release}
Summary: lantern source code
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
BuildArch: noarch
%endif

%description devel
lantern source code

%package -n %{name}-ui-devel
%if 0%{?with_build}
Requires: %{name}
%endif
Summary: lantern-ui source code
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
BuildArch: noarch
%endif

%description -n %{name}-ui-devel
lantern-ui source code

%prep
%setup -q -n %repo-%{_commit}
rm -rf src/github.com/getlantern/pac-cmd/binaries \
    src/gopkg.in/check.v1 \
    src/github.com/hashicorp/golang-lru \
    src/github.com/skratchdot/open-golang/open \
    src/github.com/davecgh/go-spew/spew \
    src/github.com/kardianos/osext \
    src/code.google.com/p/go-uuid/uuid \
    src/github.com/gorilla/websocket
sed -i '/kardianos/s|github.com|bitbucket.org|g' \
    src/github.com/getlantern/go-update/update.go \
    src/github.com/getlantern/go-update/check/check.go \
    src/github.com/getlantern/launcher/launcher_darwin.go \
    src/github.com/getlantern/launcher/launcher_windows.go

%build
export GOPATH=%{gopath}

build_tags='prod'
%if 0%{?with_headless}
build_tags+=' headless'
%endif
sed -e '/packageVersion/s|=.*|= "%{version}"|' -e 's|!prod|prod|' \
    src/github.com/getlantern/flashlight/autoupdate.go > \
    src/github.com/getlantern/flashlight/autoupdate-prod.go

logger_token=$(sed -n '/^LOGGLY_TOKEN /s|.*=[[:space:]]\(.*\)$|\1|p' Makefile)
ldflags="-s -w -X \"main.version=%{_shortcommit}\" \
    -X \"main.revisionDate=%{_revision_date}\" \
    -X \"main.buildDate=%{_build_date}\" \
    -X \"github.com/getlantern/flashlight/logging.logglyToken=${logger_token}\""

%if 0%{?with_build}
CGO_ENABLED=1 GOOS=linux GOARCH=%{arch} \
go build -a -v -o %{repo}_linux_%{arch} -tags="$build_tags" \
    -ldflags="${ldflags} -linkmode internal -extldflags \"-static\"" \
    github.com/getlantern/flashlight
%endif

%install
%if 0%{?with_build}
installer_resources='./installer-resources/linux'
packaged_yaml='.packaged-lantern.yaml'
packaged_settings='startupurl:'

install -Dm755 %{repo}_linux_%{arch} %{buildroot}%{_libdir}/%{repo}/%{repo}-binary
install -Dm755 ${installer_resources}/%{repo}.sh %{buildroot}%{_libdir}/%{repo}
echo "$packaged_settings" > %{buildroot}%{_libdir}/%{repo}/${packaged_yaml}
touch %{buildroot}%{_libdir}/%{repo}/%{repo}.yaml

install -d %{buildroot}%{_bindir}
ln -sfv %{_libdir}/%{repo}/%{repo}.sh %{buildroot}%{_bindir}/%{repo}
ln -sfv %{_libdir}/%{repo}/%{repo}-binary %{buildroot}%{_bindir}/%{repo}-bin

# systemd service file
install -d %{buildroot}%{_userunitdir}
cat > %{buildroot}%{_userunitdir}/%{repo}.service <<EOF
[Unit]
Description=%{Summary}
Documentation=https://github.com/getlantern/lantern
After=network.target

[Service]
Type=simple
ExecStart=%{_bindir}/%{repo} -headless -addr 127.0.0.1:8787
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target
EOF

# desktop and icon files
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{repo}.desktop <<EOF
[Desktop Entry]
Type=Application
Name=%{repo}
Exec=%{repo}
Icon=%{repo}
EOF

install -Dm644 ${installer_resources}/icon*.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{repo}.png
%endif

# lantern source code
install -d %{buildroot}%{gopath}
# find all *.go but no *_test.go files and generate devel.file-list
for ext in go cfg c s js map html scss less css json topojson conf yaml tmpl gif png svg ico webp jpeg bmp tiff otf woff h cpp def; do
    for file in $(find src -type f -and -iname "*.${ext}" \! -iname "*_test.go"); do
        install -D $file %{buildroot}%{gopath}/$file
        echo "%%{gopath}/$file" >> devel.file-list
    done
done
# remove unit test files
for dir in $(find %{buildroot} -iname "testdata" -or -iname "example*"); do
    rm -rf $dir
done

sort -u -o devel.file-list devel.file-list
sed -E -i '/(testdata|example*|%{name}-ui)/d' devel.file-list

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:
/usr/bin/update-desktop-database &>/dev/null ||:
%systemd_user_post %{repo}.service

%preun
%systemd_user_preun %{repo}.service

%postun
if [ $1 -eq 0 ]; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:
    /usr/bin/gtk-update-icon-cache -f -t -q %{_datadir}/icons/hicolor ||:
fi
/usr/bin/update-desktop-database &>/dev/null ||:

%posttrans
/usr/bin/gtk-update-icon-cache -f -t -q %{_datadir}/icons/hicolor ||:

%if 0%{?with_build}
%files
%defattr(-,root,root,-)
%doc README.md
%{_bindir}/%{repo}*
%{_libdir}/%{repo}/
%{_datadir}/applications/%{repo}.desktop
%{_datadir}/icons/hicolor/*/apps/%{repo}.png
%{_userunitdir}/%{repo}.service
%endif

%files devel -f devel.file-list
%defattr(-,root,root,-)

%files -n %{name}-ui-devel
%defattr(-,root,root,-)
%{gopath}/src/github.com/get%{repo}/%{repo}-ui/

%changelog
* Fri Feb  5 2016 mosquito <sensor.wen@gmail.com> - 2.0.11-2.gitfdff338
- Add source code subpackage
* Thu Feb  4 2016 mosquito <sensor.wen@gmail.com> - 2.0.11-1.gitfdff338
- Initial build