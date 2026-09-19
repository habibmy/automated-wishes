# automated-wishes

> A self-hosted, modular birthday and anniversary wisher powered by your CardDAV contacts.

**Status: Early concept / architecture discussion**

I'm exploring a self-hosted application that automatically sends birthday and anniversary wishes to selected contacts.

The idea is simple:

**Use the contacts you already maintain in CardDAV as the source of truth, detect birthdays/anniversaries, generate a message, and deliver it through whatever notification service you prefer.**

This project is currently in the design stage. I'm sharing the concept before implementing it to get feedback from the self-hosted/homelab community.

---

## Why?

Most birthday reminder systems require maintaining a separate list of birthdays.

But if you already use a CardDAV address book, your contacts may already contain:

- Name
- Phone number
- Birthday
- Anniversary
- Groups/categories
- Notes

So why maintain the same information twice?

I'd like the application to simply use the existing CardDAV address book.

For example:

> Add a person's birthday to your contacts → put them in the `Wishes` group → the application handles the rest.

---

## Basic idea

```text
                    CardDAV
                       │
                       ▼
                Read contacts
                       │
                       ▼
                 Apply filters
                       │
                       ▼
              Detect today's events
                       │
              ┌────────┴────────┐
              ▼                 ▼
           Birthday         Anniversary
              │                 │
              └────────┬────────┘
                       ▼
                Generate message
                       │
                       ▼
                 Delivery layer
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Apprise        WhatsApp       HTTP/SMS
        │              │              │
        ▼              ▼              ▼
   ntfy, Telegram,   WhatsApp      SMS gateway
   email, etc.       gateway
```

The important part is that **the core application should not depend on any particular messaging platform.**

---

# CardDAV as the source of truth

The application would read contacts directly from a CardDAV server.

Examples could include:

- Baïkal
- Nextcloud
- Radicale
- iCloud
- Other CardDAV-compatible servers

Relevant vCard properties include:

```text
FN
TEL
BDAY
ANNIVERSARY
CATEGORIES
NOTE
UID
```

The application should not require users to manually create a second birthday database.

---

# Selecting who receives wishes

I don't want the application to automatically message every contact in an address book.

Instead, contacts could be selected using CardDAV groups/categories.

For example:

```text
Family
Friends
Work
Wishes
No Wishes
```

A simple configuration could be:

```yaml
groups:
  include:
    - Wishes

  exclude:
    - No Wishes
```

This means the address book itself becomes the user interface for deciding who is eligible.

There could also be a local blocklist for cases where an individual contact needs to be excluded without changing the CardDAV address book.

---

# Birthday and anniversary events

The CardDAV data would be converted into normalized events internally.

For example:

```json
{
  "contact_id": "abc123",
  "name": "Rahul Sharma",
  "phone": "+9198XXXXXXXX",
  "event_type": "birthday",
  "date": "2026-09-19",
  "years": 28
}
```

An anniversary could look like:

```json
{
  "contact_id": "xyz789",
  "name": "Rahul & Priya",
  "phone": "+9198XXXXXXXX",
  "event_type": "anniversary",
  "date": "2026-09-19",
  "years": 5
}
```

The rest of the application would work with these normalized events rather than directly with CardDAV fields.

This should make the system easier to extend later.

---

# Message templates

Messages should be configurable rather than hard-coded.

For example:

```yaml
templates:
  birthday:
    - "Happy Birthday {{name}}! 🎂 Wishing you a wonderful year ahead!"

  anniversary:
    - "Happy Anniversary {{name}}! ❤️ Wishing you many more happy years together!"
```

Possible variables could include:

```text
{{name}}
{{first_name}}
{{event_type}}
{{age}}
{{years}}
{{date}}
```

Multiple templates could optionally be used so the same message isn't sent every year.

An AI-based message generator could potentially be added later, but it would not be required for the core system.

---

# Notification / delivery layer

This is one of the main design goals.

The application should have a provider/adapter system rather than being tied to one messaging platform.

Possible providers:

### Apprise

Use Apprise as a general notification backend.

This would potentially provide access to services such as:

- ntfy
- Telegram
- Discord
- email
- Pushover
- and many others

Instead of implementing every service individually.

### WhatsApp

A separate adapter could talk to a locally hosted WhatsApp gateway.

For example:

```text
automated-wishes
       │
       ▼
WhatsApp provider
       │
       ▼
local WhatsApp REST API
```

The application shouldn't care whether that gateway is implemented using Go, Node, Baileys, WhatsApp Web, or something else.

### HTTP / SMS gateway

A generic HTTP provider could allow users to connect arbitrary SMS gateways.

For example:

```yaml
providers:
  sms:
    type: http
    method: POST
    url: "http://192.168.1.20:8080/send"
```

The exact API format would be configurable.

This could also make it possible to integrate custom services without writing a new provider.

### SMTP

Email could be another simple provider.

### Dry run

A dry-run provider would allow testing without actually sending anything.

Example:

```text
[DRY RUN]

Birthday:
Rahul Sharma
+91XXXXXXXXXX

Message:
Happy Birthday Rahul! 🎂 Wishing you a wonderful year ahead!
```

---

# Delivery scheduling

The application shouldn't necessarily send everything immediately at midnight.

For example:

```yaml
schedule:
  timezone: Asia/Kolkata

  delivery_window:
    start: "08:00"
    end: "10:00"
```

If someone has a birthday today, the application could wait until the configured delivery window.

There could also be configurable delivery pacing between messages.

This is useful for users who have many contacts and don't want all messages sent at exactly the same time.

---

# Reliability

Automatic messaging needs to be predictable.

The application should keep local state, probably using SQLite.

For example:

```text
contact UID
event type
event date/year
provider
status
timestamp
```

This allows the application to know:

> "I already sent Rahul's 2026 birthday wish."

If the application restarts, it should not send the same message again.

The system should also track failures and potentially retry failed deliveries.

---

# Preview

Before enabling automatic sending, the user should be able to see what the application intends to do.

For example:

```text
Upcoming wishes
────────────────────────────────────

19 Sep
🎂 Rahul Sharma
   WhatsApp

22 Sep
💍 Amit & Neha
   SMS

25 Sep
🎂 Sameer
   Apprise → Telegram
```

This should make it easy to verify CardDAV groups, dates and provider configuration before enabling automatic delivery.

---

# Example deployment

The intended deployment would be simple and self-hosted.

Something along the lines of:

```text
Docker
│
├── automated-wishes
│
└── SQLite
```

External services could be connected separately:

```text
CardDAV server
      │
      ▼
automated-wishes
      │
      ├── Apprise
      ├── WhatsApp gateway
      ├── SMTP
      └── HTTP/SMS gateway
```

The application itself would not need to host every messaging service.

---

# Design principles

The project is currently being designed around a few principles:

### 1. CardDAV-first

Contacts should remain the source of truth.

### 2. Self-hosted

No central cloud service should be required.

### 3. Modular

Users should be able to choose how messages are delivered.

### 4. Provider agnostic

WhatsApp should not be treated as the core transport.

### 5. Safe by default

No accidental mass messaging.

### 6. Idempotent

Restarting the application should not cause duplicate wishes.

### 7. Configurable

Users should be able to control groups, templates, schedules and providers.

### 8. Simple deployment

Docker should ideally be enough to run it.

---

# What this is NOT

This is not intended to become:

- A full contact manager
- A replacement for CardDAV
- A WhatsApp client
- A CRM
- A general-purpose automation platform
- A social media automation tool

The goal is deliberately narrow:

> **Take important dates from contacts and reliably send personalized wishes through a user-selected delivery mechanism.**

---

# Questions I'm currently trying to answer

This is still an architecture discussion, so I'm particularly interested in feedback on:

### CardDAV

- Is CardDAV a reasonable source of truth for this?
- Which CardDAV servers should be tested?
- Are there important vCard birthday/anniversary edge cases I'm missing?

### Contact selection

Would a CardDAV group such as `Wishes` be a good mechanism?

Or would people prefer configuration-based rules?

### Delivery

Would an Apprise provider cover most notification use cases?

Would a generic HTTP provider be useful for SMS gateways and custom services?

### WhatsApp

For people self-hosting WhatsApp gateways, would a generic REST provider be preferable to supporting a particular implementation?

### Reliability

What failure/retry/idempotency behavior would you expect from a daemon like this?

### Architecture

Are there existing projects solving this problem in a way I should look at before building another one?

---

# Current status

**Early concept / architecture stage.**

No implementation decisions are considered final yet.

I'm primarily looking for feedback from people who run self-hosted services, CardDAV servers, notification systems, or similar automation.

If something similar already exists, I'd much rather use or contribute to an existing project than unnecessarily create another one.
