---
public: "true"
tags:
  - "#htb"
  - "#CVE-2025-24071"
  - Active-Directory
  - Windows
  - "#coercion"
created-at: 2026-04-01
---

# Information

- Machine name: Fluffy
- OS: Windows
- Difficulty: Easy

# Attack Path

- Access to IT share as initial (provided user)
- The share has a few zip files and a PDF alerting to the presence of CVE-2025-24071 among others.
- This is a vulnerability to force user authentication via SMB when extracting a malicious zip file. The exploit code is available [here](https://github.com/FOLKS-iwd/CVE-2025-24071-msfvenom).
- Create a malicious zip, start responder and intercept the resulting hash for user p.agila. This can be cracked to obtain the password.
- The user is part of `Service Account Managers` group which has `GenericAll` over `Service Accounts`. This group in turn has `GenericWrite` over the three service accounts `winrm_svc`, `ldap_svc` and `ca_svc`.
- We can make `p.agila` part of the `Service Accounts` group and create shadow credentials for the three service accounts to dump the NTLM hashes.
- `winrm_svc` can PSRemote on the DC, giving the user flag.
- Abuse [ESC16](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation#esc16-security-extension-disabled-on-ca-globally) (this wasn't detected by my version of `certipy-ad`, so I had to look it up). Exploiting is straightforward in this case. `ca_svc` can change their UPN to `administrator`, request a `User` certificate, change their UPN back and use the PFX for authenticaiton. This dumps the NTLM hash of `administrator`.

# Lessons Learned

- Keep your tools up to date
- Learned a bit about ADCS
- User auth coercion via CVE-2025-24071
