# ⚡ PredictBR — Tech Setup Guide

## 🚀 Quick Start Development Setup

### **📋 Infrastructure Accounts** (Setup Today)

**Essential Services**:
```bash
# Hosting & Database  
✅ Vercel (Frontend) → vercel.com
✅ Railway (Backend) → railway.app  
✅ Supabase (PostgreSQL) → supabase.com

# Development
✅ GitHub (Private repos) → github.com/orgs
✅ Clerk (Authentication) → clerk.dev
✅ Sentry (Error tracking) → sentry.io

# Payments & Web3
✅ Polygon RPC → polygon.technology
✅ MetaMask integration → docs.metamask.io
✅ USDC Contract → 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
```

### **🏗️ Project Structure**

```
predictbr/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # Node.js backend  
├── packages/
│   ├── ui/                  # Shared components
│   ├── types/               # TypeScript definitions
│   └── config/              # Shared configuration
├── docs/
│   ├── api/                 # API documentation
│   └── deployment/          # Deployment guides
└── tools/
    ├── scripts/             # Development scripts
    └── migrations/          # Database migrations
```

---

## 🛠️ Tech Stack Implementation

### **Frontend (Next.js)**

**Package.json essentials**:
```json
{
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0", 
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "latest",
    "wagmi": "^1.4.0",
    "viem": "^1.21.0",
    "zustand": "^4.5.0",
    "react-query": "^3.39.0",
    "framer-motion": "^10.18.0"
  }
}
```

**Key configurations**:
```typescript
// next.config.js
const nextConfig = {
  experimental: {
    appDir: true,
  },
  webpack: (config) => {
    config.resolve.fallback = { fs: false, net: false, tls: false };
    return config;
  },
}

// tailwind.config.js  
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#10B981', // Green
        secondary: '#3B82F6', // Blue  
        danger: '#EF4444', // Red
      }
    }
  }
}
```

### **Backend (Node.js)**

**Essential dependencies**:
```json
{
  "dependencies": {
    "express": "^4.18.0",
    "typescript": "^5.3.0", 
    "@types/express": "^4.17.0",
    "prisma": "^5.8.0",
    "@prisma/client": "^5.8.0",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "rate-limiter-flexible": "^4.0.0",
    "viem": "^1.21.0",
    "ws": "^8.16.0"
  }
}
```

**Database Schema (Prisma)**:
```prisma
// schema.prisma
model User {
  id        String   @id @default(cuid())
  wallet    String   @unique
  email     String?  
  createdAt DateTime @default(now())
  
  positions Position[]
  orders    Order[]
}

model Market {
  id          String   @id @default(cuid())
  title       String
  description String
  category    String
  endDate     DateTime
  resolved    Boolean  @default(false)
  outcome     Boolean? 
  
  positions Position[]
  orders    Order[]
}

model Position {
  id       String @id @default(cuid())
  userId   String
  marketId String
  outcome  Boolean // true = YES, false = NO
  shares   Decimal
  
  user   User   @relation(fields: [userId], references: [id])
  market Market @relation(fields: [marketId], references: [id])
}

model Order {
  id       String   @id @default(cuid())
  userId   String
  marketId String  
  outcome  Boolean
  shares   Decimal
  price    Decimal
  filled   Boolean  @default(false)
  createdAt DateTime @default(now())
  
  user   User   @relation(fields: [userId], references: [id])
  market Market @relation(fields: [marketId], references: [id])
}
```

---

## 🔗 Web3 Integration

### **Polygon USDC Setup**

```typescript
// lib/web3.ts
import { createConfig, http } from 'wagmi'
import { polygon } from 'wagmi/chains'
import { metaMask } from 'wagmi/connectors'

export const config = createConfig({
  chains: [polygon],
  connectors: [metaMask()],
  transports: {
    [polygon.id]: http(process.env.NEXT_PUBLIC_POLYGON_RPC_URL),
  },
})

// USDC Contract (Polygon)
export const USDC_CONTRACT = {
  address: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
  abi: [
    'function transfer(address to, uint256 amount) returns (bool)',
    'function balanceOf(address owner) view returns (uint256)',
    'function allowance(address owner, address spender) view returns (uint256)',
    'function approve(address spender, uint256 amount) returns (bool)'
  ]
} as const
```

### **Payment Flow Implementation**:

```typescript
// lib/payments.ts
import { parseUnits, formatUnits } from 'viem'

export class PaymentService {
  async deposit(amount: number, userWallet: string) {
    // 1. User approves USDC spending
    // 2. Transfer USDC to platform wallet  
    // 3. Update user balance in database
    // 4. Emit deposit event
  }
  
  async withdraw(amount: number, userWallet: string) {
    // 1. Verify user balance
    // 2. Transfer USDC to user wallet
    // 3. Update database  
    // 4. Emit withdrawal event
  }
}
```

---

## 📊 Core Features Implementation

### **Order Matching Engine**

```typescript  
// lib/orderbook.ts
export class OrderBook {
  private buyOrders: Order[] = []
  private sellOrders: Order[] = []
  
  addOrder(order: Order) {
    if (order.outcome) {
      this.buyOrders.push(order)
      this.buyOrders.sort((a, b) => b.price - a.price) // Desc
    } else {
      this.sellOrders.push(order) 
      this.sellOrders.sort((a, b) => a.price - b.price) // Asc
    }
    
    this.matchOrders()
  }
  
  private matchOrders() {
    while (this.buyOrders.length && this.sellOrders.length) {
      const buyOrder = this.buyOrders[0]
      const sellOrder = this.sellOrders[0]
      
      if (buyOrder.price >= sellOrder.price) {
        this.executeTrade(buyOrder, sellOrder)
      } else {
        break
      }
    }
  }
}
```

### **Market Resolution**

```typescript
// lib/resolution.ts  
export class MarketResolution {
  async resolveMarket(marketId: string, outcome: boolean) {
    // 1. Mark market as resolved
    // 2. Calculate payouts for winning positions
    // 3. Update user balances
    // 4. Emit resolution event
    
    await prisma.market.update({
      where: { id: marketId },
      data: { resolved: true, outcome }
    })
    
    const winningPositions = await prisma.position.findMany({
      where: { marketId, outcome }
    })
    
    // Distribute winnings...
  }
}
```

---

## 🎨 UI Components (Shadcn)

### **Market Card Component**:

```tsx
// components/market-card.tsx
interface MarketCardProps {
  market: {
    id: string
    title: string
    yesPrice: number
    noPrice: number
    volume: number
  }
}

export function MarketCard({ market }: MarketCardProps) {
  return (
    <Card className="p-4 hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="text-sm font-medium">
          {market.title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center">
          <Button 
            variant="outline" 
            className="bg-green-50 border-green-200"
          >
            SIM {market.yesPrice}¢
          </Button>
          <Button 
            variant="outline"
            className="bg-red-50 border-red-200" 
          >
            NÃO {market.noPrice}¢
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Volume: R${market.volume.toLocaleString()}
        </p>
      </CardContent>
    </Card>
  )
}
```

### **Trading Interface**:

```tsx
// components/trading-panel.tsx
export function TradingPanel({ marketId }: { marketId: string }) {
  const [outcome, setOutcome] = useState<boolean>(true)
  const [amount, setAmount] = useState<number>(0)
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Fazer Aposta</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex space-x-2">
            <Button 
              variant={outcome ? "default" : "outline"}
              onClick={() => setOutcome(true)}
            >
              SIM
            </Button>
            <Button 
              variant={!outcome ? "default" : "outline"}
              onClick={() => setOutcome(false)}
            >
              NÃO
            </Button>
          </div>
          
          <Input 
            type="number"
            placeholder="Valor em USDC"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
          />
          
          <Button className="w-full" onClick={handleTrade}>
            Apostar R${amount}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

---

## 🔒 Security Essentials

### **Rate Limiting**:
```typescript
// lib/rate-limit.ts
import { RateLimiterMemory } from 'rate-limiter-flexible'

const rateLimiter = new RateLimiterMemory({
  points: 100, // Number of requests
  duration: 60, // Per 60 seconds
})

export const rateLimit = async (req: Request, res: Response, next: NextFunction) => {
  try {
    await rateLimiter.consume(req.ip)
    next()
  } catch {
    res.status(429).json({ error: 'Too many requests' })
  }
}
```

### **Input Validation**:
```typescript
// lib/validation.ts
import { z } from 'zod'

export const OrderSchema = z.object({
  marketId: z.string().cuid(),
  outcome: z.boolean(), 
  shares: z.number().positive().max(10000),
  price: z.number().min(0.01).max(0.99)
})

export const validateOrder = (data: unknown) => {
  return OrderSchema.parse(data)
}
```

---

## 🚀 Deployment Configuration

### **Vercel (Frontend)**:
```json
// vercel.json
{
  "builds": [
    { "src": "next.config.js", "use": "@vercel/next" }
  ],
  "env": {
    "NEXT_PUBLIC_POLYGON_RPC_URL": "@polygon-rpc-url",
    "NEXT_PUBLIC_API_URL": "@api-url"
  }
}
```

### **Railway (Backend)**:
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### **Environment Variables**:
```bash
# .env.example
DATABASE_URL="postgresql://..."
CLERK_SECRET_KEY="sk_..."
POLYGON_RPC_URL="https://polygon-rpc.com"
PLATFORM_WALLET_PRIVATE_KEY="0x..."
SENTRY_DSN="https://..."
```

---

## 📋 Development Checklist

### **Week 1 (22-28 Feb)**:
- [ ] Setup all infrastructure accounts
- [ ] Create GitHub organization + repos
- [ ] Deploy basic Next.js app to Vercel
- [ ] Deploy basic Express API to Railway  
- [ ] Setup Supabase database + Prisma
- [ ] Configure Clerk authentication
- [ ] Basic UI components (Shadcn)

### **Week 2 (1-7 Mar)**:  
- [ ] User registration + wallet connection
- [ ] Database models + API endpoints
- [ ] USDC deposit/withdrawal flow
- [ ] Basic order book implementation
- [ ] Market creation admin panel

### **Week 3 (8-14 Mar)**:
- [ ] Frontend ↔ Backend integration
- [ ] Market trading interface
- [ ] Portfolio/dashboard
- [ ] Real-time updates (WebSocket)
- [ ] Market resolution workflow

### **Week 4 (15-21 Mar)**:
- [ ] End-to-end testing
- [ ] Security review + rate limiting
- [ ] Performance optimization
- [ ] Production deployment
- [ ] 3 markets creation + launch

---

**🎯 Target: All infrastructure setup by 24 Feb → Development starts 25 Feb**

*Need help with specific implementation? I can provide detailed code examples for any component.*