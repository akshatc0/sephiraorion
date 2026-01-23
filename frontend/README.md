# Sephira Orion - Modern Chat Frontend

## Overview

A modern, chat-first interface for Sephira Orion built with Next.js 14, featuring inline visualizations and beautiful animations.

## Features

- **Single-Page Chat Interface**: All interactions happen in one beautiful conversation
- **Smart Predictions**: Ask natural questions, get predictions with inline charts
- **Inline Visualizations**: 
  - Forecast charts
  - Trend analysis cards
  - Correlation matrices
  - Anomaly detection lists
- **Animated UI**: Framer Motion animations throughout
- **Responsive Design**: Works perfectly on mobile and desktop
- **Persistent Chat**: Conversations saved locally

## Tech Stack

- **Next.js 14** (App Router)
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Recharts** for data visualization
- **Zustand** for state management
- **Axios** for API calls

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main chat page
│   └── globals.css         # Global styles
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx    # Main orchestrator
│   │   ├── ChatInput.tsx        # Input with animations
│   │   ├── MessageBubble.tsx    # Message rendering
│   │   └── AnimatedBackground.tsx # Gradient background
│   ├── visualizations/
│   │   ├── InlineForecast.tsx   # Forecast chart
│   │   ├── InlineTrends.tsx     # Trends cards
│   │   ├── InlineCorrelation.tsx # Correlation matrix
│   │   └── InlineAnomalies.tsx  # Anomaly list
│   └── ui/
│       └── LoadingDots.tsx      # Loading animation
├── lib/
│   ├── api.ts              # API client
│   ├── store.ts            # Zustand store
│   ├── types.ts            # TypeScript types
│   └── utils.ts            # Utility functions
└── public/
    └── audio/
        └── send2.wav       # Send sound effect (optional)
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## How It Works

### Chat-First Design

Instead of separate pages for each feature, everything is accessible through natural conversation:

- **"Forecast Russia for 30 days"** → Shows forecast chart inline
- **"Show me trends in Asia"** → Displays trend analysis cards
- **"How do USA and China correlate?"** → Renders correlation matrix
- **"Detect any anomalies"** → Lists detected anomalies

### Intent Detection

The frontend analyzes your message to determine which predictions to fetch:

- Keywords like "forecast", "predict", "future" → Forecast API
- Keywords like "trend", "pattern", "movement" → Trends API
- Keywords like "correlate", "compare", "relationship" → Correlation API
- Keywords like "anomaly", "unusual", "outlier" → Anomalies API

### Smart Responses

The AI (Sephira Orion) provides contextual answers and automatically includes relevant visualizations in the conversation.

## Color Scheme

From the template design:

- **Background**: `#F5F6F6` (Light warm gray)
- **Cards**: `#FFFFFF` (White)
- **Secondary**: `#f5f4f3` (Button backgrounds)
- **AI Messages**: `#0ea5e9` (Sky-500 blue)
- **User Messages**: White with soft shadow

### Animated Gradient Colors

- Pink: `#FC2BA3`
- Orange: `#FC6D35`
- Yellow: `#F9C83D`
- Light Blue: `#C2D6E1`
- Deep Blue: `#144EC5`

## API Integration

The frontend connects to the FastAPI backend (http://localhost:8000) and uses these endpoints:

- `POST /api/chat` - Main chat interface
- `POST /api/predict/forecast` - Time series forecasting
- `POST /api/predict/trends` - Trend analysis
- `POST /api/predict/correlations` - Correlation analysis
- `POST /api/predict/anomalies` - Anomaly detection

## State Management

Uses Zustand for:
- Message history (persisted to localStorage)
- Loading states
- Selected countries
- Date ranges

Messages are automatically saved and restored on page reload.

## Performance

- Lazy loading of visualization components
- Optimized animations with GPU acceleration
- Code splitting for faster initial loads
- Production build ~160 KB First Load JS

## Audio Feedback (Optional)

Place a `send2.wav` file in `public/audio/` for sound effects when sending messages. The app will work fine without it.

## Development

### Adding New Visualizations

1. Create component in `components/visualizations/`
2. Add type to `lib/types.ts`
3. Import in `MessageBubble.tsx`
4. Add detection logic in `ChatInterface.tsx`

### Customizing Colors

Edit `tailwind.config.ts` to change the color scheme.

### Modifying Intent Detection

Update `lib/utils.ts` > `detectIntent()` function.

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Troubleshooting

### Build Errors

- Clear `.next` folder: `rm -rf .next`
- Clear cache: `npm run clean` (add script if needed)
- Reinstall: `rm -rf node_modules && npm install`

### API Connection Issues

- Ensure backend is running on port 8000
- Check `.env.local` has correct API URL
- Verify CORS is enabled in backend

### Animation Performance

- Ensure GPU acceleration is enabled in browser
- Reduce motion in system settings disables animations
- Test in production build (optimized)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

Part of Sephira Orion sentiment analysis system.
