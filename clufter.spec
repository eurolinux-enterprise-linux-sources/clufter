Name:           clufter
Version:        0.11.2
Release:        1%{?dist}
Group:          System Environment/Base
Summary:        Tool/library for transforming/analyzing cluster configuration formats
License:        GPLv2+
URL:            https://github.com/jnpkrn/%{name}

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-lxml

Source0:        https://people.redhat.com/jpokorny/pkgs/%{name}/%{name}-%{version}.tar.gz

%description
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.

%package cli
Group:          System Environment/Base
Summary:        Tool for transforming/analyzing cluster configuration formats

# cannot get bash-completion from EPEL6 into the buildroot
#BuildRequires:  bash-completion

BuildRequires:  help2man

# following for pkg_resources module
Requires:       python-setuptools
Requires:       python-%{name} = %{version}-%{release}
Provides:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description cli
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.

This package contains %{name} command-line interface for the underlying
library (packaged as python-%{name}).

%package -n python-%{name}
Group:          System Environment/Libraries
Summary:        Library for transforming/analyzing cluster configuration formats
License:        GPLv2+ and GFDL

BuildRequires:  pkgconfig(libxml-2.0)

Requires:       python-lxml
Requires:       %{_bindir}/nano

%description -n python-%{name}
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.

This package contains %{name} library including built-in plugins.

%package lib-general
Group:          System Environment/Libraries
Summary:        Extra %{name} plugins usable for/as generic/auxiliary products
Requires:       python-%{name} = %{version}-%{release}
BuildArch:      noarch

%description lib-general
This package contains set of additional plugins targeting variety of generic
formats often serving as a byproducts in the intermediate steps of the overall
process arrangement: either experimental commands or internally unused,
reusable formats and filters.

%package lib-ccs
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing CMAN configuration
Requires:       python-%{name} = %{version}-%{release}
Requires:       %{name}-lib-general = %{version}-%{release}
BuildArch:      noarch

%description lib-ccs
This package contains set of additional plugins targeting CMAN cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.

%package lib-pcs
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing Pacemaker configuration
Requires:       python-%{name} = %{version}-%{release}
Requires:       %{name}-lib-general = %{version}-%{release}
BuildArch:      noarch

%description lib-pcs
This package contains set of additional plugins targeting Pacemaker cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.

%prep
%setup

## for some esoteric reason, the line above has to be empty
%{__python} setup.py saveopts -f setup.cfg pkg_prepare \
                      --ccs-flatten='%{_libexecdir}/%{name}-%{version}/ccs_flatten' \
                      --editor='%{_bindir}/nano' \
                      --ra-metadata-dir='%{_datadir}/cluster' \
                      --ra-metadata-ext='metadata'

%build
%{__python} setup.py build
./run-dev --skip-ext --completion-bash 2>/dev/null \
  | sed 's|run[-_]dev|%{name}|g' > .bashcomp
%{__mkdir_p} -- .manpages/man1
help2man -N -h -H -n "$(sed -n '2s|[^(]\+(\([^)]\+\))|\1|p' README)" ./run-dev \
  | sed 's|run[-_]dev|%{name}|g' \
  > .manpages/man1/%{name}.1

%install

# '--root' implies setuptools involves distutils to do old-style install
%{__python} setup.py install --skip-build --root '%{buildroot}'
# following is needed due to umask 022 not taking effect(?) leading to 775
%{__chmod} -- g-w '%{buildroot}%{_libexecdir}/%{name}-%{version}/ccs_flatten'
# %%{_bindir}/%%{name} should have been created
test -f '%{buildroot}%{_bindir}/%{name}' \
  || %{__install} -D -pm 644 -- '%{buildroot}%{_bindir}/%{name}' \
                                '%{buildroot}%{_bindir}/%{name}'
declare bashcompdir="$(pkg-config --variable=completionsdir bash-completion \
                       || echo '%{_sysconfdir}/bash_completion.d')"
declare bashcomp="${bashcompdir}/%{name}"
%{__install} -D -pm 644 -- \
  .bashcomp '%{buildroot}%{_sysconfdir}/%{name}/bash-completion'
%{__mkdir_p} -- "%{buildroot}${bashcompdir}"
ln -s '%{_sysconfdir}/%{name}/bash-completion' "%{buildroot}${bashcomp}"
# own %%{_datadir}/bash-completion in case of ...bash-completion/completions,
# more generally any path up to any of /, /usr, /usr/share, /etc
while true; do
  test "$(dirname "${bashcompdir}")" != "/" \
  && test "$(dirname "${bashcompdir}")" != "%{_prefix}" \
  && test "$(dirname "${bashcompdir}")" != "%{_datadir}" \
  && test "$(dirname "${bashcompdir}")" != "%{_sysconfdir}" \
  || break
  bashcompdir="$(dirname "${bashcompdir}")"
done
cat >.bashcomp-files <<-EOF
	${bashcompdir}
	%dir %{_sysconfdir}/%{name}
	%verify(not size md5 mtime) %{_sysconfdir}/%{name}/bash-completion
EOF
%{__mkdir_p} -- '%{buildroot}%{_mandir}'
%{__cp} -a -- .manpages/* '%{buildroot}%{_mandir}'
%{__mkdir_p} -- '%{buildroot}%{_defaultdocdir}/%{name}-%{version}'
%{__install} -pm 644 -- gpl-2.0.txt doc/*.txt \
                        '%{buildroot}%{_defaultdocdir}/%{name}-%{version}'

%check
# just a basic sanity check
# we need to massage RA metadata files and PATH so the local run works
# XXX we could also inject buildroot's site_packages dir to PYTHONPATH
declare ret=0 \
        ccs_flatten_dir="$(dirname '%{buildroot}%{_libexecdir}/%{name}-%{version}/ccs_flatten')"
ln -s '%{buildroot}%{_datadir}/cluster'/*.'metadata' \
      "${ccs_flatten_dir}"
PATH="${PATH:+${PATH}:}${ccs_flatten_dir}" ./run-check
ret=$?
%{__rm} -f -- "${ccs_flatten_dir}"/*.'metadata'
[ ${ret} -eq 0 ] || exit ${ret}

%post cli
if [ $1 -gt 1 ]; then  # no gain regenerating it w/ fresh install (same result)
declare bashcomp="%{_sysconfdir}/%{name}/bash-completion"
%{_bindir}/%{name} --completion-bash > "${bashcomp}" 2>/dev/null || :
fi

%post lib-general
declare bashcomp="%{_sysconfdir}/%{name}/bash-completion"
# if the completion file is not present, suppose it is not desired
test -x '%{_bindir}/%{name}' && test -f "${bashcomp}" \
  && %{_bindir}/%{name} --completion-bash > "${bashcomp}" 2>/dev/null || :

%post lib-ccs
declare bashcomp="%{_sysconfdir}/%{name}/bash-completion"
# if the completion file is not present, suppose it is not desired
test -x '%{_bindir}/%{name}' && test -f "${bashcomp}" \
  && %{_bindir}/%{name} --completion-bash > "${bashcomp}" 2>/dev/null || :

%post lib-pcs
declare bashcomp="%{_sysconfdir}/%{name}/bash-completion"
# if the completion file is not present, suppose it is not desired
test -x '%{_bindir}/%{name}' && test -f "${bashcomp}" \
  && %{_bindir}/%{name} --completion-bash > "${bashcomp}" 2>/dev/null || :

%files cli -f .bashcomp-files
%{_mandir}/man1/*.1*
%{_bindir}/%{name}
%{python_sitelib}/%{name}/__main__.py*
%{python_sitelib}/%{name}/main.py*
%{python_sitelib}/%{name}/completion.py*

%files -n python-%{name}
%dir %{_defaultdocdir}/%{name}-%{version}
%{_defaultdocdir}/%{name}-%{version}/*[^[:digit:]].txt
%doc %{_defaultdocdir}/%{name}-%{version}/*[[:digit:]].txt
%exclude %{python_sitelib}/%{name}/__main__.py*
%exclude %{python_sitelib}/%{name}/main.py*
%exclude %{python_sitelib}/%{name}/completion.py*
%exclude %{python_sitelib}/%{name}/ext-plugins/*/
%{python_sitelib}/%{name}
%{python_sitelib}/%{name}-*.egg-info
%{_libexecdir}/%{name}-%{version}
%{_datadir}/cluster

%files lib-general
%{python_sitelib}/%{name}/ext-plugins/lib-general

%files lib-ccs
%{python_sitelib}/%{name}/ext-plugins/lib-ccs

%files lib-pcs
%{python_sitelib}/%{name}/ext-plugins/lib-pcs

%changelog
* Fri May 29 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.11.2-1
- move completion module to clufter-cli sub-package
- bump upstream package

* Mon May 18 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.11.1-1
- bump upstream package

* Wed Apr 15 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.11.0-1
- bump upstream package

* Fri Mar 20 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.3-1
- bump upstream package

* Mon Mar 16 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.2-1
- bump upstream package

* Fri Mar 06 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.1-2
- packaging fixes (%{name}-cli requires python-setuptools, adjust for
  older schema of Bash completions)

* Fri Mar 06 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.1-1
- bump upstream package

* Thu Feb 26 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.0-1
- packaging enhacements (structure, redundancy, ownership, scriptlets, symlink)
- version bump so as not to collide with python-clufter co-packaged with pcs

* Tue Jan 20 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.3.5-1
- packaging enhancements (pkg-config, license tag)

* Wed Jan 14 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.3.4-1
- packaging enhancements (permissions, ownership)
- man page for CLI frontend now included

* Tue Jan 13 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.3.3-1
- initial build
