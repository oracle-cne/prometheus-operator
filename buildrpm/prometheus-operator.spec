
%if 0%{?with_debug}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global _name	prometheus-operator
%global _comp_prefix	prometheus
%global package_name	    github.com/prometheus/%{_name}
%global _buildhost          build-ol%{?oraclelinux}-%{?_arch}.oracle.com

Name:           %{_name}
Version:        0.83.0
Release:        1%{?dist}
Summary:        The Prometheus Operator provides Kubernetes native deployment and management of Prometheus and related monitoring components.
License:        Apache 2.0
Group:          System/Management
Url:            https://github.com/prometheus/%{name}
Source:         %{name}-%{version}.tar.bz2
Vendor:         Oracle America
BuildRequires:  golang

%description
The Prometheus Operator provides Kubernetes native deployment and management of Prometheus and related monitoring components. The purpose of this project is to simplify and automate the configuration of a Prometheus based monitoring stack for Kubernetes clusters.

%prep
%setup -q -n %{name}-%{version}

%build
export GOPATH=$(go env GOPATH)
GOPATH_SRC=$GOPATH/src/%{package_name}
%__mkdir_p $GOPATH_SRC
%__rm -r $GOPATH_SRC
%__ln_s $PWD $GOPATH_SRC
%__mkdir_p %{_builddir}/%{name}-%{version}/output/bin/

pushd $GOPATH_SRC
cd ${GOPATH_SRC}
GIT_REVISION=5cf2f5d37906d64b2259a262e319df4c74639e31
BUILD_USER=${BUILD_USER:-"${USER}@%{_buildhost}"}
BUILD_DATE=${BUILD_DATE:-$( date +%Y%m%d-%H:%M:%S )}
ldflags="
        -X main.version=v%{version}
        -X github.com/prometheus/common/version.Version=%{version}
        -X github.com/prometheus/common/version.Revision=${GIT_REVISION}
        -X github.com/prometheus/common/version.Branch=HEAD
        -X github.com/prometheus/common/version.BuildUser=${BUILD_USER}
        -X github.com/prometheus/common/version.BuildDate=${BUILD_DATE}"
# Prometheus Operator build
go build -trimpath=false -v -o %{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-operator \
    -ldflags "${ldflags}" \
    ${GOPATH_SRC}/cmd/operator
%{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-operator --version
# Prometheus Config Reloader build
go build -v -o %{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-config-reloader \
    -ldflags "${ldflags}" \
    ${GOPATH_SRC}/cmd/%{_comp_prefix}-config-reloader
%{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-config-reloader --version
# Prometheus Admission Webhook build
go build -v -o %{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-admission-webhook \
    -ldflags "${ldflags}" \
    ${GOPATH_SRC}/cmd/admission-webhook
%{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-admission-webhook --version

%install
install -d -m 755 %{buildroot}%{_bindir}
install -p -m 755 -t %{buildroot}%{_bindir}/ %{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-operator
install -p -m 755 -t %{buildroot}%{_bindir}/ %{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-config-reloader
install -p -m 755 -t %{buildroot}%{_bindir}/ %{_builddir}/%{name}-%{version}/output/bin/%{_comp_prefix}-admission-webhook

%files
%{_bindir}/%{_comp_prefix}-operator
%{_bindir}/%{_comp_prefix}-config-reloader
%{_bindir}/%{_comp_prefix}-admission-webhook
%license LICENSE NOTICE THIRD_PARTY_LICENSES.txt olm/SECURITY.md
%doc README.md

%clean
rm -fr %{buildroot}
rm -fr %{_builddir}/%{name}-%{version}

%changelog
* Thu Aug 28 2025 Olcne-Builder Jenkins <olcne-builder_us@oracle.com> - 0.83.0-1
- Added Oracle-specific build files.
