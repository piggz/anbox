Name:       anbox-sailfishos
Summary:    Run Android inside a container
Version:    1
Release:    1
Group:      System/Applications
License:    LGPL 2.1
URL:        https://github.com/anbox/anbox
Source:     %{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  mesa-llvmpipe-libEGL-devel
BuildRequires:  mesa-llvmpipe-libGLESv2-devel
BuildRequires:  SDL2-devel
BuildRequires:  SDL2_image-devel
BuildRequires:  dbus-cpp-devel
BuildRequires:  lxc-devel
BuildRequires:  wayland-devel
BuildRequires:  mesa-llvmpipe-libEGL-devel
BuildRequires:  systemd-devel
BuildRequires:  protobuf-compiler
BuildRequires:  boost-devel
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  protobuf-lite-devel
BuildRequires:  properties-cpp-devel
BuildRequires:  pkgconfig(libcap)

Requires:  boost-filesystem
Requires:  boost-iostreams
Requires:  boost-system
Requires:  boost-thread
Requires:  boost-program-options
Requires:  anbox-sailfishos-image
Requires:  boost-log
Requires:  lxc
Requires:  protobuf
Requires:  libprocess-cpp2

%define debug_package %{nil}

%description
  Runtime for Android applications which runs a full Android system
  in a container using Linux namespaces (user, ipc, net, mount) to
  separate the Android system fully from the host.

%prep
%setup -q -n %{name}-%{version}/anbox

%build
truncate -s 0 cmake/FindGMock.cmake
truncate -s 0 tests/CMakeLists.txt

#Allow cmake 3.11
sed -i 's/cmake_minimum_required/#cmake_minimum_required/g' external/sdbus-cpp/CMakeLists.txt

mkdir -p build  
cd build
%cmake -DUSE_SFDROID=ON -DBUILD_TESTING=OFF ..
make %{?jobs:-j%jobs}

%install
rm -rf %{buildroot}
pushd build
%make_install
popd

install -Dm 755 scripts/prepare-anbox.sh %{buildroot}/%{_bindir}/prepare-anbox
install -Dm 644 %{_sourcedir}/anbox-container-manager.service %{buildroot}/%{_libdir}/systemd/system/anbox-container-manager.service
install -Dm 644 %{_sourcedir}/anbox-session-manager.service %{buildroot}/%{_libdir}/systemd/user/anbox-session-manager.service
install -Dm 644 %{_sourcedir}/anbox-bridge.network %{buildroot}/%{_libdir}/systemd/network/80-anbox-bridge.network
install -Dm 644 %{_sourcedir}/anbox-bridge.netdev %{buildroot}/%{_libdir}/systemd/network/80-anbox-bridge.netdev
install -Dm 644 rpm/99-anbox.rules %{buildroot}/%{_libdir}/udev/rules.d/99-anbox.rules
install -Dm 644 %{_sourcedir}/anbox.desktop %{buildroot}/%{_datadir}/applications/anbox.desktop
install -Dm 644 snap/gui/icon.png %{buildroot}/%{_datadir}/icons/hicolor/512x512/apps/anbox.png

%post
#if [ "$1" -ge 1 ]; then
#    systemctl-user daemon-reload || true
#    systemctl-user restart anbox-session-manager.service || true
#fi
prepare-anbox

%postun
#if [ "$1" -eq 0 ]; then
#    systemctl-user stop anbox-session-manager.service || true
#    systemctl-user daemon-reload || true
#fi
#TODO: Add cleanup-anbox script too, to cleanup after anbox

%files
%defattr(-,root,root,-)
#%doc README COPYING
%{_bindir}/anbox
%{_bindir}/prepare-anbox

%{_libdir}/systemd/system/anbox-container-manager.service
%{_libdir}/systemd/user/anbox-session-manager.service
%{_libdir}/systemd/network/80-anbox-bridge.network
%{_libdir}/systemd/network/80-anbox-bridge.netdev
%{_libdir}/udev/rules.d/99-anbox.rules
%{_datadir}/applications/anbox.desktop
%{_datadir}/icons/hicolor/512x512/apps/anbox.png
%{_datadir}/anbox/ui/loading-screen.png
 
