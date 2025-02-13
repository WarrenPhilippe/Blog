---
title: "Microsoft Exchange Client Access Server Information Disclosure: The "Oops, Here’s My Internal IP" Bug"
author: "Jamie Warren Philippe"
date: "2025-02-13"
categories: [Cybersecurity, Disclosure, Exploits, Microsoft]
tags: [Microsoft, Exchange, Information Attack, Disclosure, Exploitation]
---
# Microsoft Exchange Client Access Server Information Disclosure: The "Oops, Here’s My Internal IP" Bug

## The Scene: An External Pentest Gone Too Well
Ah, Microsoft Exchange—the gift that keeps on giving. During an external penetration test, I stumbled upon an information disclosure bug that made recon a breeze. Instead of sweating over OSINT and pivoting through obscure DNS leaks, the Exchange Client Access Server (CAS) decided to just *hand me* its internal IP like a confused mall security guard giving out the WiFi password.

## The Setup: IIS 10.0, HTTP/1.0, and a Misconfigured Host Header
The server was running **IIS 10.0**, and I found that if you send a good ol’ **HTTP/1.0** request while supplying an **empty Host header**, the response would include some juicy internal information—specifically, the private IP address of the server, neatly tucked away in the **WWW-Authenticate realm header**.

## The "Elite" Exploit (a.k.a. Running Curl)
This is one of those exploits where you don’t need a fancy zero-day or an obscure Python script. Nope, just some good old **curl**:

```bash
curl -X GET http://target.com/owa/ -H "Host:" --http1.0 -i
```

### Expected Response:
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Negotiate
WWW-Authenticate: NTLM realm="192.168.1.50"
```

Oh no, Exchange! You weren’t supposed to **tell me that!**

## Why This Works: Exchange + IIS Being "Helpful"
By default, Exchange CAS servers running on **IIS 10.0** love to respond to authentication requests in a way that includes the internal realm. Normally, this isn’t an issue—unless, of course, someone forgot to properly configure the headers and now **every unauthenticated request leaks the internal network structure**.

And let’s be honest: most admins are too busy fighting Outlook issues to bother with security headers.

## The "Why Should You Care?" Section
What can an attacker do with an internal IP? Well, for starters:
- **Refine attack paths:** Knowing the internal structure makes pivoting much easier.
- **Bypass some poorly configured security policies:** If there's a split-tunnel VPN or weak firewall rules, this can be gold.
- **Social engineering fuel:** "Oh hey, IT helpdesk? Yeah, I’m calling from 192.168.1.50, we got a problem..." *NGL, I lacked some inspiration on that one*

## How to Fix This (If You’re an Admin and Now Panicking)
Luckily, this one’s an easy fix (assuming you don’t ignore it like that pile of pending updates on your test server):

1. **Disable NTLM authentication over HTTP (force it over HTTPS)**
2. **Set up proper response headers to avoid leaking internal details**
3. **Use a reverse proxy or WAF to filter and block HTTP/1.0 requests**
4. **Audit Exchange CAS configurations (because this probably isn’t the only issue)**

## Final Thoughts
It’s 2025, and Microsoft Exchange is *still* finding new ways to embarrass itself. But hey, if you’re a pentester, it’s free recon with minimal effort—so thanks, Exchange, for making external engagements just a little bit easier. 🎉

---

**Next Up:** "From Directory Listing to Webshell to Domain Admin—Because Why Make It Hard?"