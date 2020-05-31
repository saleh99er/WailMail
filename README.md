# WailMail

The best way to get notified of incoming mail. Receive real-time audio notifications of arriving emails depending on if that email matches certain word occurences. Intended to be run on a Raspberry Pi but also compatible with Windows and Linux.

Inspired by Atsu and Hacklarious Hackathon hosted by MLH

### Getting Started

``` git clone https://github.com/saleh99er/WailMail.git```

### Prerequisites

* Computer to run Wail Mail
    * Raspberry Pi
        * AUX output device (HDMI or AUX)
    * Windows
    * Ubuntu (with mpg123 installed)

* LAN network (router, preferably assigns private IP addresses to all hosts)
* Python 3
    packages:
    * imapclient
    * email
    * flask
    * mutagen
* Git
* Additional MP3 files if desired


### Installing / Setup

#### Raspberry Pi

Setup your pi headless (provide LAN configuration, allow SSH, etc). [Directions](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)

#### Windows

Install python 3 and the packages in prerequisites (pip).

#### Common

Clone / Download the repository (former preferred). 

``` git clone https://github.com/saleh99er/WailMail.git ```

Connect your host device to an audio output. Navigate to `audio` directory on your terminal and confirm the audio is audible for your system.

* Raspberry Pi: ```omxplayer -o both megolovania_short.mp3```
* Ubuntu : ```mpg123 megolovania_short.mp3```
* Windows 10 : ``` start megolovania_short.mp3```

Record your host device's local/private IP address.
    * For Ubuntu / Raspberry pi use `ifconfig` and look for your address in the `inet` field from the interface used to connect to your LAN (wlan, ethX, etc.).
    * For Windows 10 use `ipconfig` and look for your address in the `IPv4 Address` field. 

Create an app password for WailMail and store the IMAP domain name, your email address, and app password in `user.txt` within the main directory. [Gmail App Password] (https://support.google.com/accounts/answer/185833?hl=en)

Example:
```
imap.gmail.com
<your gmail address>
<your app password>
```

Have at least one unread email in your inbox and confirm that as you execute ```python3 emailClientReader_test.py``` the subject of these unread emails appear within the print statements. 

Navigate back to the program's main directory and start it with ```python3 WailMail.py```. 

Now on any device connected to the same LAN, navigate to `<Wail Mail Host IP>:5000` on a web browser. From this webpage you can set rules for word occurences and what audio file should be played if those word occurences occur.

The rules use pseudo-python syntax where parentheses, `and`, `or`, and `^` are reserved. Any other 'term' within the subject, from, and body fields are checked and if it occurs at least once, that 'term' in the rule's expression would evaluate to `True`, `False` otherwise. A 'term' is any string that doesn't match the reserved words, that do not have any spaces in between characters. Example: 'foo' and 'somebody@someone.com' are words but 'foo bar' is not. If the entire expression evaluates to `True` then the audio file located to the right of the arrow will be played. 

Lastly, the ide number is the portion to the left of the colon to identify each rule, only one simaltaneous rule can exist with that id number. 

Example:

```
1: hello and world -> screaming_sheep.mp3 
```

Here if we receive any emails with the word occurences of 'hello' and 'world', then the audio file screaming_sheep.mp3 will be played. Note substrings with these words will not cause these to evaluate their respective words to true (hello_world, worldwide, hello_there). The rules are case-insensitive and insensitive to how the words are ordered / located in the email. 

### Q & A

Overall view of how Wail Mail works?
    * There are 4 modules each can be seen as it's own thread where they are all isolated except for the interconnecting queues and an end event. Email Client Reader (ECR) periodically fetches new unread emails from the IMAP server and puts them in the email queue. The flask thread acts as a web server that allows the user to interact with Wail Mail via web browser. Any valid rules the user creates is put in the rule queue. The flask thread can also set the end event. The email parser takes from the email and rule queues and determines if any emails match any rules, if so, schedule an audio filename to be played by placing the filename in the audio queue. Lastly the audio player thread will take from the audio queue and plays the file if present in `static/audio`.

Why did you do Wail mail this way?
    * To be honest, this project was thrown together and I'd appreciate feedback/questions on how I put it together. I wanted to make something somewhat beginner friendly where anyone comfortable with Python and multithreading could understand how it works.

What state is stored in WailMail?

    * Any rules set by the user are only persistent for that session, power cycling or terminating the program can cause the previous session rules to be lost. Audio files in `static/audio` will not be affected. Refreshing the webpage does not cause the rule state to be reset. 

## Roadmap

Other features not supported yet but under consideration are present on the Github issues page [here](https://github.com/saleh99er/WailMail/issues). By cloning the repository you can pull new changes and enjoy the new features without repeating the setup. 

## Support

If you have any issues, file an issue on the repository [here](https://github.com/saleh99er/WailMail/issues) and I'll try to get back to you on it.  

## Acknowledgements

Thanks Atsu for the inspiration on this project and thank you developers of [imapclient](https://imapclient.readthedocs.io/en/2.1.0/) for your library, streamlining the development needed to make this project possible. Also thanks StackOverflow, StackExchange, and countless other resources for debugging / solutions to problems I ran into along the way.

## License
[MIT](https://choosealicense.com/licenses/mit/)