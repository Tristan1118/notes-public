---
public: "true"
tags:
  - "#htb"
  - Windows
  - Active-Directory
created-at: 2026-04-01
---

# Information

- Machine name: Scepter
- OS: Windows
- Difficulty: Hard

# Lessons Learned

## Impersonation Issues:

h.brown:

```
bloodyAD --dc-ip 10.10.11.65 -k -d scepter.htb --host dc01.scepter.htb get object h.brown

distinguishedName: CN=h.brown,CN=Users,DC=scepter,DC=htb
accountExpires: 1601-01-01 00:00:00+00:00
altSecurityIdentities: X509:<RFC822>h.brown@scepter.htb
badPasswordTime: 1601-01-01 00:00:00+00:00
```

p.adams:

```
bloodyAD --dc-ip 10.10.11.65 -k -d scepter.htb --host dc01.scepter.htb get object p.adams

distinguishedName: CN=p.adams,OU=Helpdesk Enrollment Certificate,DC=scepter,DC=htb
accountExpires: 1601-01-01 00:00:00+00:00
badPasswordTime: 1601-01-01 00:00:00+00:00
```

p.adams doesn't have the `altSecurityIdentities` attribute set. Therefore, the impersonation attack only works on h.brown.
