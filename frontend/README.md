# Mental Coach Frontend

A modern Next.js frontend for the Mental Coach chat application. This frontend provides a beautiful, user-friendly interface for interacting with the AI-powered mental coach backend.

## Features

- 🎨 Modern, responsive UI with gradient design
- 💬 Real-time chat interface with message history
- ⚡ Fast and efficient with Next.js 14
- 📱 Mobile-friendly responsive design
- 🎯 Clear visual distinction between user and assistant messages
- ⚠️ Comprehensive error handling and user feedback
- 🔄 Loading states and smooth animations

## Prerequisites

- Node.js 18+ and npm (or yarn/pnpm)
- The backend API running on `http://localhost:8000` (see `/api/README.md` for backend setup)

## Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```
   
   Or if you're using yarn:
   ```bash
   yarn install
   ```
   
   Or if you're using pnpm:
   ```bash
   pnpm install
   ```

3. **Configure the API URL (optional):**
   
   By default, the frontend connects to `http://localhost:8000`. If your backend is running on a different URL, create a `.env.local` file in the `frontend` directory:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## Running the Application

### Development Mode

1. **Make sure the backend is running:**
   
   From the project root, start the backend server:
   ```bash
   uv run uvicorn api.index:app --reload
   ```
   
   The backend should be running on `http://localhost:8000`.

2. **Start the frontend development server:**
   
   From the `frontend` directory:
   ```bash
   npm run dev
   ```
   
   Or with yarn:
   ```bash
   yarn dev
   ```
   
   Or with pnpm:
   ```bash
   pnpm dev
   ```

3. **Open your browser:**
   
   Navigate to [http://localhost:3000](http://localhost:3000) to see the application.

   The page will automatically reload when you make changes to the code.

### Production Build

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Start the production server:**
   ```bash
   npm start
   ```

   The application will be available at [http://localhost:3000](http://localhost:3000).

## Project Structure

```
frontend/
├── app/                    # Next.js App Router directory
│   ├── layout.tsx         # Root layout component
│   ├── page.tsx           # Main chat page component
│   ├── page.module.css    # Styles for the chat page
│   └── globals.css        # Global styles
├── lib/                   # Utility functions
│   └── api.ts            # API client for backend communication
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── next.config.js        # Next.js configuration
└── README.md             # This file
```

## How It Works

1. **Chat Interface**: The main page (`app/page.tsx`) provides a chat interface where users can type messages and receive responses from the AI mental coach.

2. **API Communication**: The `lib/api.ts` file handles all communication with the FastAPI backend, sending POST requests to `/api/chat` with user messages.

3. **State Management**: React hooks (`useState`, `useEffect`) manage the chat messages, loading states, and error handling.

4. **Styling**: CSS Modules provide scoped styling for components, ensuring good visual clarity and contrast as per design requirements.

## Troubleshooting

### Frontend can't connect to backend

- Ensure the backend is running on `http://localhost:8000`
- Check that the `OPENAI_API_KEY` environment variable is set for the backend
- Verify CORS is properly configured in the backend (it should allow all origins in development)

### Port 3000 is already in use

- Kill the process using port 3000:
  ```bash
  lsof -ti:3000 | xargs kill -9
  ```
- Or run the dev server on a different port:
  ```bash
  npm run dev -- -p 3001
  ```

### Build errors

- Make sure all dependencies are installed: `npm install`
- Clear the `.next` directory and rebuild: `rm -rf .next && npm run build`
- Check that you're using Node.js 18 or higher

## Deployment

This frontend is designed to be deployed on Vercel. See the main project README for deployment instructions.

When deploying, make sure to set the `NEXT_PUBLIC_API_URL` environment variable in your Vercel project settings to point to your deployed backend API URL.

## Technologies Used

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **CSS Modules**: Scoped component styling
- **React Hooks**: State and effect management
