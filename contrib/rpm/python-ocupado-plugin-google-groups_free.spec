# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?__python2: %global __python2 %__python}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

Name:           python-ocupado-plugin-google-groups_free
Version:        0.0.1
Release:        1%{?dist}
Summary:        Google Groups plugin for ocupado

License:        AGPLv3+
URL:            https://github.com/ashcrow/ocupado_plugin_google_groups_free
Source0:        ocupado_plugin_google_groups_free-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python-ocupado, PyOpenSSL, python-mechanize

%description
Google Groups (free version) plugin for the ocupado tool.


%prep
%setup -qc
mv ocupado_plugin_google_groups_free-%{version} python2

%build
pushd python2
%{__python2} setup.py build
popd

%install
rm -rf $RPM_BUILD_ROOT
pushd python2
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
popd

%files
%doc python2/AUTHORS python2/COPYING python2/LICENSE python2/README.md
# For noarch packages: sitelib
%{python2_sitelib}/*

%changelog
* Wed Jul 22 2015 Steve Milner <stevem@gnulinux.net> - 0.0.1-1
- Initial spec.
