# Debian/Ubuntu VPS Simple & Basic Initial Hardening Playbook

This Ansible playbook is designed to take a freshly rented, insecure Debian/Ubuntu VPS (accessible only via `root` with a password) and transform it into a secure, hardened environment in a single run.

## What this playbook does:
1. **System Updates:** Updates all system packages to their latest versions.
2. **Installs Dependencies:** Installs `sudo`, `ufw` (Firewall), `fail2ban` (Intrusion Prevention), and `unattended-upgrades`.
3. **Installs Docker:** Configures Docker's official APT repository, installs Docker Engine with Buildx and Compose plugins, and enables the Docker service.
4. **User Management:** Creates a secure, non-root user, grants them passwordless `sudo` access (ideal for future Ansible automation), and adds them to the `docker` group.
5. **SSH Keys:** Injects your local public SSH key into the new user's `authorized_keys`.
6. **Firewall:** Enables UFW, blocking all incoming traffic except SSH.
7. **Intrusion Prevention:** Enables Fail2Ban to automatically temporarily ban IPs that attempt to brute-force SSH.
8. **SSH Hardening:** 
- PermitRootLogin no
- PubkeyAuthentication yes
- X11Forwarding no
- MaxAuthTries 3
- ClientAliveInterval
- AllowUsers {{ new_user }}
- PasswordAuthentication no

---

## Important Nuances & Safety Features

* **Anti-Lockout Validation:** The playbook uses `validate: /usr/sbin/sshd -t -f %s` before applying changes to the SSH daemon. If the playbook makes a syntax error, SSH will refuse the change rather than crashing and locking you out. 
* **Sudoers Best Practices:** Instead of modifying the main `/etc/sudoers` file (which can be risky and overwrite OS defaults), this playbook safely places a dedicated file in `/etc/sudoers.d/`.
* **Docker Access:** Membership in the `docker` group is effectively root-level access. Sign out and back in after the playbook runs before using Docker without `sudo`.

---

## Requirements

**On your Local Machine:**
* [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) installed.
* `sshpass` installed (required for Ansible to log in with a password the very first time). 
  * *Ubuntu/Debian:* `sudo apt install sshpass`
  * *macOS:* `brew install sshpass`
* An SSH Keypair. If you don't have one, generate it:
  `ssh-keygen -t ed25519 -C "vps-admin"`


---

## How to use this Playbook

### Step 1: Configure Variables
1. Configure `inventory.ini` 
2. Edit `vars.yml` and adjust the variables:
   * `new_user`: The name of the user you want to create (e.g., `adminuser`).
   * `ssh_public_key_path`: The path to your **local** public key (e.g., `~/.ssh/id_ed25519.pub`).

### Step 2: Establish a "Lifeline" (CRITICAL SAFETY STEP)
Because this playbook disables password login, if your SSH key is invalid, you could lock yourself out. 
Before running the playbook, open a terminal window and SSH into your VPS:
```bash
ssh root@<YOUR_VPS_IP>
```
(Or make a snapshot of your system before running this playbook)
### Step 3: Run the playbook 
E.g. `ansible-playbook -i inventory.ini harden.yml -k` (if running for the first time) 
`ansible-playbook -i inventory.ini harden.yml --limit=yandex_cloud -vv` (running playbook against yandex_cloud host)
