# BabylonPolice the SourceAvailable proof of transparency for BabylonPolice.com

## Preambling

We believe in a reverse-KYC policy, meaning that any potentially-skeptical potentially-anonymous potential-client is less likely to want to use your products and services if you implement KYC, and further less likely if you do not implement reverse KYC, meaning at the very least SourceAvailable, or OpenSource.

By seeing how we operate, you will know that we can be trusted (so far as we remain committed to such a policy) to offer the best of services and products, clean and transparent, without any risk to the client. Just as Offshore Trust Funds are set up in numerous jurisdictions (known as Tax Havens) without income tax, without inheritance tax, without capital gains tax, without estate tax, purely and simply because it brings them in more money. This supports my idea that is: "The more laws, rules, and policies you implement to define what is wrong, incorrect, or punishable, the less support you will have from your people." And it's analog in Truth "The more things you say are True, the less likely you are of being correct."

## Introduction

This is the SourceAvailable form of BabylonPolice.com which you can copy, and build, and implement yourselves, so long as you follow the LICENSE.md, but the main point of SourceAvailable is for transparency and security, honesty and integrity, trust and for your own protection.

User-customisable dictionaries and spaces, a mix of urban-dictionary and reddit, but payments are in cryptocurrency.


# Vision

## Where We Want To Be

We want to be aligned morally and ethically as a company with the corporate sector, as well as with stakeholders and shareholders. We want to be guided by firstly family, and then friends close enough to be considered family, before we decide about when and how much to open up to outside investors. We want to be on the same side as those around us.

## How We Want To Get There

To get there we need to be open an honest about our relationships where we are divulging intellectual property. We want to prove transparency amongst those who use our platform, ie. the customers. We want to show that we aren't saving your passwords or credit card information, we want to show updates live as connected to the platform changes, so that there's nothing missing between what happens and what we can prove is what happening.

# Mission

## What We Aim To Do

We aim to put our clients first. As a social media that means not making money without our customers making money. So advertisers don't pay unless they get results. We don't sell anything ourselves, only take a cut from content curators earning.

## Who We Aim To Help

We aim to help content curators to earn from forwarding their clients onto other resources. So long as you are comfortable with the order of content being curated and what is there, you can make an income with or without also being the content creator. Turn your feed into feeds for others.

We also aim to help prominent Urban Dictionary slang-writers to sell and privatise their content.

# For Investors

Take a brief scan over the to-do list, if you have questions, ask, if you have suggestions tell. Your input is my security, I'm banking on your criticisms being valid and important. Until we launch as a company instead of just a business there will be no shares in writing, but consideration will be made for those have provided value as referred to by other investor parties.

# Quick Scan and Example Infrastructure

https://www.babylonpolice.com/B/user/test/dictionary/be_here_now/word/inconsistory/count/0/ This is an example of what defining a word looks like without signing in, and if you sign in and click on the attribute, because it is selected as available to the public, you can see other attributes beyond just the definition.

# To do list:

## Implement End-to-End-to-End encryption.

### (includes reasoning for)
Most end-to-end encryption, like protonmail.com, dnmx.org, signal, wickr, silksafe, pryvate, signal, whatsapp, telegram, line, dust, viber, threema, silent phone, wire, imessage, facetime, kakaotalk, outlook, tutanota, mailfence, hushmail, etc etc. aren't actually secure just because they say they implement end-to-end encryption. And let me go into this. All implementations of E2EE so far (aside from Dark Net Markets that use PGP), hold onto your private keys. It's the same rule as with Crypto. Not your key's not your coins, AKA not your private keys not your privacy.

So. We will implement an email encryption service that is double encrypted. Once between our servers and databases to which we hold the private keys, to keep our databases from being easily combed through, but the thing is, we still hold the private keys in the database, and we can't do that in plain text. So we will have to encrypt those ourselves with an environment variable, so not only do they have to get into the database, but they also have to get into the server. And then we'll create a client-side encryption-decryption script that you can see, and test, and ensure that you can encrypt-decrypt the messages between anyone who uses our services, and YOU HOLD THE PRIVATE KEYS. People who don't use our services will either have to encrypt their own messages to your public address, or not use E2EE, however, we will still encrypt it on our end-to-end. Web applications are not just one end to another. There is an SQL database URL (text, numbers), there is a server URL, and then there is a file-databse URL (images, videos, etc). The difference is, SQL is readily searchable, has metadata, and stores the ID's of the files in the file-database, so that they can be input into a URL and loaded by the client. Imagine if the website you were using had to load every image from the database and then send it to you, NO, imagine how inefficient that would be, we have an old term for this "Double Handling". So ideally you would encrypt between each end that communicates with every other end, with each end holding unique private keys for each scenario.

The highest grade of encryption out there is OpenPGP at 4096 bits, ie. 1234 decimal digits, with the first numbers being 104438888... the reason being that the higher the number, the harder it is to find a prime number. And yet [the largest known prime number](https://primes.utm.edu/curios/page.php?number_id=12089) has 244862048 digits, and it's been confirmed many times since it was discovered in... 2018. They have a database of all the prime numbers up to 1234 decimal digits, I guarantee it. And [the distribution of prime numbers](https://brilliant.org/wiki/distribution-of-primes/) is such that for any integer number N, the probability that number is prime is prime is 1/ln(N). ie the probability that 2^512 is prime is 1/355, or 1/177 if we exclude odd numbers. So it turns out the number of primes up to N is N/ln(N), and then set N to 2^4096, we learn that there is a number of 1229 digits starting with 367855141... So yeah, good luck finding your particular prime number there, and cracking your encryption. But if you don't have the private keys...


If you look at wikipedia, even they don't get this:

```
Some encrypted backup and file sharing services provide client-side encryption. The encryption they offer is here not referred to as end-to-end encryption, because the services are not meant for sharing messages between users[further explanation needed]. However, the term "end-to-end encryption" is sometimes incorrectly used to describe client-side encryption.
```
And they cite the following paper:
```
https://www.researchgate.net/publication/342621891_Improving_Non-Experts%27_Understanding_of_End-to-End_Encryption_An_Exploratory_Study

10.1109/EuroSPW51379.2020.00036


```
And guess who wrote it. Employees at Google. And if you go through the Appendix C.1 almost ALL of the anonymized clients mention that the messages are privately encrypted between the client and the server. 

Although wikipedia is quoting something that isn't actually said in the article, "they confuse it with client-side-encryption", the term "client-side-encryption" was never mentioned in the article, so not even the researchers themselves were making mention of it. Client to server is still end-to-end. My end, your end. That's end-to-end. So to make this distinction we will call it end-to-end-to-end encryption. We will encourage you to use an OpenSource, locally backed up password manager.... if there's even a good one.

Which brings me to my next point.

## Build a cross-platform mobile app

SourceAvailable in-built with a mail app, where you hold your private keys locally on the device, and then you can export them.

It looks like we'll be using [tutanota](https://github.com/tutao/tutanota) as that is the best base to start from, however there are a lot of features missing.

## Implement user-specific clickthrough id's

This allows for tracking who forwarded someone to your dictionary or space, allowing the dictionary or space owner to pay-it-forward for who referred who to your system.

## Custom Font and Moving Text for in-text word referencing.

Allows for fonts and jiggling text to have specific meanings.

## Users Vote History

This allows for votes to work as endorsements whether it's a positive or negative or other support framework.

## Embed YouTube and TikTok videos

Include more content curation ability.

## Crypto currency payments for content creators / curators.

## Search Auto Complete with every known word (vertically stacked) in every known category of words (other verbs, other nouns, other nouns alphabetically).

## Make Mutawords as having a mechanism

### One such mechanism:

Prediction sort -- using frequency, match occurrence with word length.

#### Sequential sort -- using permutation types:

Match least consonants, match least phonemes, match quickest to say

-- Then remove letters from the selectors - no c, no k, and so on.

Rebuild a type-set for words of a given length with a selector algorithm to compare uniques.


TODO:

Build in bulk billing for spaces. Revamp spaces page.


