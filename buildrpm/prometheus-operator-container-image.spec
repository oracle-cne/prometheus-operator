
%global debug_package   %{nil}
%{!?registry: %global registry container-registry.oracle.com/olcne}

%global _name	prometheus-operator
%global _comp_prefix	prometheus
%global _buildhost build-ol%{?oraclelinux}-%{?_arch}.oracle.com

Name:       %{_name}-container-image
Version:    0.83.0
Release:    1%{?dist}
Summary:    The Prometheus Operator provides Kubernetes native deployment and management of Prometheus and related monitoring components.
License:    Apache 2.0
Url:        https://github.com/prometheus/%{name}
Source:     %{name}-%{version}.tar.bz2
Vendor:     Oracle America

%description
The Prometheus Operator provides Kubernetes native deployment and management of Prometheus and related monitoring components. The purpose of this project is to simplify and automate the configuration of a Prometheus based monitoring stack for Kubernetes clusters.

%prep
%setup -q -n %{name}-%{version}

%build

%define dockerfile "Dockerfile"

%__rm -f .dockerignore
yum clean all

rpms=(%{_comp_prefix}-operator-%{version}-%{release} %{_comp_prefix}-operator-%{version}-%{release} %{_comp_prefix}-operator-%{version}-%{release})
tags=(%{_comp_prefix}-operator %{_comp_prefix}-config-reloader %{_comp_prefix}-admission-webhook)
for i in ${!rpms[@]}; do
  yumdownloader --destdir=${PWD}/rpms ${rpms[i]}

  docker_tag="%{registry}/${tags[i]}:v%{version}"
  docker build --pull \
      --build-arg https_proxy=${https_proxy} \
      -t ${docker_tag} -f ./olm/builds/%{dockerfile}.${tags[i]} .
  docker save -o ${tags[i]}.tar ${docker_tag}
  rm -rf ${PWD}/rpms
done

%install
%__install -D -m 644 %{_name}.tar %{buildroot}/usr/local/share/olcne/%{_comp_prefix}-operator.tar
%__install -D -m 644 prometheus-config-reloader.tar %{buildroot}/usr/local/share/olcne/%{_comp_prefix}-config-reloader.tar
%__install -D -m 644 prometheus-admission-webhook.tar %{buildroot}/usr/local/share/olcne/%{_comp_prefix}-admission-webhook.tar

%files
%license LICENSE NOTICE THIRD_PARTY_LICENSES.txt olm/SECURITY.md
/usr/local/share/olcne/%{_comp_prefix}-operator.tar
/usr/local/share/olcne/%{_comp_prefix}-config-reloader.tar
/usr/local/share/olcne/%{_comp_prefix}-admission-webhook.tar

%changelog
* Thu Aug 28 2025 Olcne-Builder Jenkins <olcne-builder_us@oracle.com> - 0.83.0-1
- Added Oracle-specific build files.
