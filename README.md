# Santa Claus Bot

Santa Claus Bot is a Python-based Discord bot designed to bring holiday joy to users by providing interactive features such as evaluating behavior, responding to messages, and analyzing images sent by users.

## Features

- **Interactive Messaging:** The bot evaluates messages to determine whether the user has been "naughty" or "nice."
- **Image Analysis:** Leverages OpenAI's video analysis API to interpret images, such as detecting messy rooms or identifying objects.
- **Session-Based Logging:** Tracks and logs user activity with session identifiers for enhanced debugging and tracking.

## Requirements

- Python 3.10 or higher
- Discord.py library
- OpenAI API key (for image and text analysis)
- Additional dependencies (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/KraverekPL/SantaClausBot.git
   cd SantaClausBot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add the following variables:
     ```env
     DISCORD_TOKEN=your_discord_bot_token
     OPENAI_API_KEY=your_openai_api_key
     LOG_LEVEL=INFO
     ```

## Usage

Run the bot using the following command:
```bash
python main.py
```

## File Structure

```
SantaClausBot/
├── modules/
│   ├── reactionCog.py   # Handles reactions and bot responses
│   ├── analysis.py      # Image and text analysis logic
├── main.py              # Entry point of the bot
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
└── README.md            # Documentation
```

## Contributing

Contributions are welcome! Feel free to fork this repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact [KraverekPL](https://github.com/KraverekPL).
