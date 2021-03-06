Name:           deepin-gtk-theme
Version:        17.10.3
Release:        1%{?dist}
Summary:        Deepin GTK Theme
License:        LGPLv3
URL:            https://github.com/linuxdeepin/deepin-gtk-theme
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz
BuildArch:      noarch

%description
Deepin GTK Theme

%prep
%setup -q

%build

%install
%make_install PREFIX=%{_prefix}

%files
%doc README.md
%license LICENSE
%{_datadir}/themes/deepin/
%{_datadir}/themes/deepin-dark/

%changelog
* Fri Jul 14 2017 mosquito <sensor.wen@gmail.com> - 17.10.3-1.git6140502
- Update to 17.10.3

* Fri May 19 2017 mosquito <sensor.wen@gmail.com> - 17.10.2-1.giteba2cf4
- Update to 17.10.2

* Tue Jan 17 2017 mosquito <sensor.wen@gmail.com> - 15.12.8-1.git9fd5f70
- Update to 15.12.8

* Sun Sep 18 2016 Jaroslav <cz.guardian@gmail.com> Stepanek
- Initial package build
