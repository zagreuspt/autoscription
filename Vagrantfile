# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "gusztavvargadr/windows-server"
    # config.vm.box = "gusztavvargadr/windows-10"
    config.vm.synced_folder ".", "/vagrant"
    # config.vm.guest = :windows
    # config.vm.communicator = "winrm"
    # config.vm.network "public_network", ip: "192.168.1.142", bridge: "Ethernet adapter Ethernet"
    # config.vm.network "forwarded_port", guest: 3389, host: 3389
  
    config.vm.provider "virtualbox" do |vb|
      vb.gui = true
      vb.memory = "8192"
      vb.cpus = 4
      automount = true
    end
    # config.vm.provision "shell", path: "create-users.ps1", privileged: true

  end
