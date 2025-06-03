---
title: How It Works
type: docs
prev: docs/business-context/
next: docs/architecture/
weight: 1
---

## Functionality

### Sign On

The application uses a standard authentication flow powered by Amazon Cognito. New users will need to create an account before accessing the system's functionality.

#### Account Creation Process
1. From the sign-in page, select "Create an account"
2. Enter your email address and create a secure password
3. Submit the form to initiate account verification
4. Check your email for a verification code
5. Enter the verification code on the confirmation screen
6. Optionally, you may set up sign-in with a passkey for enhanced security and convenience
7. Once verified, you'll be automatically redirected to the application landing page
<br></br>
{{< cards >}}
  {{< card link="/docs/images/pq-signin.png" title="Application Sign on Page" image="/docs/images/pq-signin.png">}}
  {{< card link="/docs/images/pq-home.png" title="Application Landing Page" image="/docs/images/pq-home.png">}}
{{< /cards >}}

After signing in, users arrive at the landing page where they can choose between two primary functions: identifying similar parliamentary questions that have been previously answered to establish precedent, or drafting a new AI-assisted response complete with citations from official source materials.

### Question Intake & Similar Question Detection

When an analyst enters a new parliamentary question into the web interface, the system automatically analyses the content and identifies similar questions that have been previously answered. This allows analysts to quickly establish precedent and maintain consistency in government responses.

![Similar](/docs/images/pq-similar.png "Similar Questions Interface User Interface: System displays the current question alongside previously answered questions ranked by similarity") 

### AI-Assisted Drafting

With a click of a button, the system generates draft responses based on official parliamentary documents. Each draft includes citations to source materials, ensuring transparency and verifiability.

![Drafting](/docs/images/pq-chat.png "AI-Assisted Drafting User Interface: AI-generated draft with source citations ready for analyst review")


