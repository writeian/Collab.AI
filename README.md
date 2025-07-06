# AI Collab 🤖💬

A modern, multi-user AI chat application built with Flask, SQLAlchemy, and OpenAI API. Users can create, share, and collaborate on AI-powered conversations with advanced features like user authentication, chat sharing, and real-time AI responses.

## ✨ Features

- **Multi-User Support**: Register, login, and manage user profiles
- **AI Chat Integration**: Powered by OpenAI GPT-4o for intelligent responses
- **Chat Management**: Create, edit, delete, and organize your conversations
- **Sharing & Collaboration**: Share chats with other users with customizable permissions
- **Public/Private Chats**: Make chats public for community discovery or keep them private
- **Modern UI**: Clean, responsive design with intuitive user experience
- **Real-time Messaging**: Seamless conversation flow with AI assistant

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/writeian/Collab.AI.git
   cd Collab.AI
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

## 📁 Project Structure

```
AI_Collab/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── openai_utils.py        # OpenAI API integration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── LICENSE               # MIT License
├── Static/
│   └── style.css         # CSS styling
└── Templates/
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── profile.html      # User profile
    ├── create_chat.html  # Create new chat
    ├── view_chat.html    # View chat conversation
    ├── edit_chat.html    # Edit chat settings
    └── share_chat.html   # Share chat with users
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `SECRET_KEY`: Flask secret key for sessions (optional, defaults to "dev")

### Database

The application uses SQLite by default. The database file (`ai_collab.db`) will be created automatically in the `instance/` directory on first run.

## 🎯 Usage

### Getting Started

1. **Register an account** at `/register`
2. **Create your first chat** at `/create`
3. **Start chatting** with the AI assistant
4. **Share chats** with other users for collaboration

### Features Overview

- **User Authentication**: Secure login/registration system
- **Chat Creation**: Create new conversations with custom titles
- **AI Integration**: Real-time responses from OpenAI GPT-4o
- **Chat Sharing**: Share conversations with specific users
- **Access Control**: Public/private chat visibility
- **User Profiles**: View and manage your account

## 🛠️ Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **AI Integration**: OpenAI API (GPT-4o)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-SQLAlchemy with password hashing
- **Styling**: Custom CSS with modern design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4o API
- Flask community for the excellent web framework
- SQLAlchemy for robust database management

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/writeian/Collab.AI/issues) page
2. Create a new issue with detailed information
3. Include your Python version, OS, and error messages

## 🔮 Roadmap

- [ ] Real-time messaging with WebSockets
- [ ] File upload and sharing
- [ ] Advanced chat analytics
- [ ] Mobile-responsive design improvements
- [ ] Multi-language support
- [ ] Chat export functionality

---

**Made with ❤️ by writeian**
