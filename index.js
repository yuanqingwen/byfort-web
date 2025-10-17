var __defProp = Object.defineProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};

// server/index.ts
import express2 from "express";

// server/routes.ts
import { createServer } from "http";
import { WebSocketServer, WebSocket } from "ws";

// server/db.ts
import { Pool, neonConfig } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-serverless";
import ws from "ws";

// shared/schema.ts
var schema_exports = {};
__export(schema_exports, {
  insertQuestionSchema: () => insertQuestionSchema,
  insertTestResultSchema: () => insertTestResultSchema,
  insertUserSchema: () => insertUserSchema,
  questions: () => questions,
  testResults: () => testResults,
  users: () => users
});
import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
var users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  deviceId: text("device_id").notNull().unique(),
  createdAt: timestamp("created_at").defaultNow().notNull()
});
var testResults = pgTable("test_results", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").notNull().references(() => users.id),
  score: integer("score").notNull(),
  correctAnswers: integer("correct_answers").notNull(),
  totalQuestions: integer("total_questions").notNull(),
  duration: integer("duration").notNull(),
  completedAt: timestamp("completed_at").defaultNow().notNull()
});
var questions = pgTable("questions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  type: text("type").notNull(),
  question: text("question").notNull(),
  options: text("options").array(),
  answer: text("answer").notNull(),
  difficulty: text("difficulty").notNull()
});
var insertUserSchema = createInsertSchema(users).omit({
  id: true,
  createdAt: true
});
var insertTestResultSchema = createInsertSchema(testResults).omit({
  id: true,
  completedAt: true
});
var insertQuestionSchema = createInsertSchema(questions).omit({
  id: true
});

// server/db.ts
neonConfig.webSocketConstructor = ws;
if (!process.env.DATABASE_URL) {
  throw new Error(
    "DATABASE_URL must be set. Did you forget to provision a database?"
  );
}
var pool = new Pool({ connectionString: process.env.DATABASE_URL });
var db = drizzle({ client: pool, schema: schema_exports });

// server/storage.ts
import { eq, desc, sql as sql2 } from "drizzle-orm";
var DbStorage = class {
  async getUser(id) {
    const result = await db.select().from(users).where(eq(users.id, id)).limit(1);
    return result[0];
  }
  async getUserByUsername(username) {
    const result = await db.select().from(users).where(eq(users.username, username)).limit(1);
    return result[0];
  }
  async getUserByDeviceId(deviceId) {
    const result = await db.select().from(users).where(eq(users.deviceId, deviceId)).limit(1);
    return result[0];
  }
  async createUser(insertUser) {
    const result = await db.insert(users).values(insertUser).returning();
    return result[0];
  }
  async createTestResult(result) {
    const inserted = await db.insert(testResults).values(result).returning();
    return inserted[0];
  }
  async getUserTestHistory(userId) {
    return await db.select().from(testResults).where(eq(testResults.userId, userId)).orderBy(desc(testResults.completedAt));
  }
  async getLeaderboard(limit = 40) {
    const results = await db.select({
      username: users.username,
      maxScore: sql2`MAX(${testResults.score})`.as("max_score"),
      testsCompleted: sql2`COUNT(${testResults.id})`.as("tests_completed")
    }).from(testResults).innerJoin(users, eq(testResults.userId, users.id)).groupBy(users.id, users.username).orderBy(desc(sql2`MAX(${testResults.score})`)).limit(limit);
    return results.map((result, index) => ({
      rank: index + 1,
      username: result.username,
      score: result.maxScore,
      testsCompleted: result.testsCompleted
    }));
  }
  async getAllQuestions() {
    return await db.select().from(questions);
  }
  async getRandomQuestions(count) {
    const allQuestions = await db.select().from(questions);
    const shuffled = allQuestions.sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count);
  }
};
var storage = new DbStorage();

// server/routes.ts
async function registerRoutes(app2) {
  const httpServer = createServer(app2);
  const wss = new WebSocketServer({
    server: httpServer,
    path: "/api/ws"
  });
  const clients = /* @__PURE__ */ new Set();
  wss.on("connection", (ws2) => {
    clients.add(ws2);
    console.log("WebSocket client connected");
    ws2.on("close", () => {
      clients.delete(ws2);
      console.log("WebSocket client disconnected");
    });
  });
  const broadcastUpdate = (type, data) => {
    const message = JSON.stringify({ type, data });
    clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  };
  setInterval(async () => {
    try {
      const leaderboard = await storage.getLeaderboard(40);
      broadcastUpdate("leaderboard", leaderboard);
    } catch (error) {
      console.error("Error broadcasting leaderboard:", error);
    }
  }, 1e3);
  app2.post("/api/users", async (req, res) => {
    try {
      const { username, deviceId } = insertUserSchema.parse(req.body);
      const existingByDevice = await storage.getUserByDeviceId(deviceId);
      if (existingByDevice) {
        return res.json(existingByDevice);
      }
      const existingByUsername = await storage.getUserByUsername(username);
      if (existingByUsername) {
        return res.status(400).json({ error: "Username sudah digunakan" });
      }
      const user = await storage.createUser({ username, deviceId });
      res.json(user);
    } catch (error) {
      res.status(400).json({ error: "Invalid request" });
    }
  });
  app2.get("/api/users/device/:deviceId", async (req, res) => {
    try {
      const user = await storage.getUserByDeviceId(req.params.deviceId);
      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }
      res.json(user);
    } catch (error) {
      res.status(500).json({ error: "Server error" });
    }
  });
  app2.post("/api/test-results", async (req, res) => {
    try {
      const data = insertTestResultSchema.parse(req.body);
      const result = await storage.createTestResult(data);
      const leaderboard = await storage.getLeaderboard(40);
      broadcastUpdate("leaderboard", leaderboard);
      const history = await storage.getUserTestHistory(data.userId);
      broadcastUpdate("history", { userId: data.userId, history });
      res.json(result);
    } catch (error) {
      console.error("Error creating test result:", error);
      res.status(400).json({ error: "Invalid request" });
    }
  });
  app2.get("/api/test-results/user/:userId", async (req, res) => {
    try {
      const history = await storage.getUserTestHistory(req.params.userId);
      res.json(history);
    } catch (error) {
      res.status(500).json({ error: "Server error" });
    }
  });
  app2.get("/api/leaderboard", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit) || 40;
      const leaderboard = await storage.getLeaderboard(limit);
      res.json(leaderboard);
    } catch (error) {
      res.status(500).json({ error: "Server error" });
    }
  });
  app2.get("/api/questions/random/:count", async (req, res) => {
    try {
      const count = parseInt(req.params.count);
      const questions2 = await storage.getRandomQuestions(count);
      res.json(questions2);
    } catch (error) {
      res.status(500).json({ error: "Server error" });
    }
  });
  return httpServer;
}

// server/vite.ts
import express from "express";
import fs from "fs";
import path2 from "path";
import { createServer as createViteServer, createLogger } from "vite";

// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import runtimeErrorOverlay from "@replit/vite-plugin-runtime-error-modal";
var vite_config_default = defineConfig({
  plugins: [
    react(),
    runtimeErrorOverlay(),
    ...process.env.NODE_ENV !== "production" && process.env.REPL_ID !== void 0 ? [
      await import("@replit/vite-plugin-cartographer").then(
        (m) => m.cartographer()
      ),
      await import("@replit/vite-plugin-dev-banner").then(
        (m) => m.devBanner()
      )
    ] : []
  ],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
      "@assets": path.resolve(import.meta.dirname, "attached_assets")
    }
  },
  root: path.resolve(import.meta.dirname, "client"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true
  },
  server: {
    fs: {
      strict: true,
      deny: ["**/.*"]
    }
  }
});

// server/vite.ts
import { nanoid } from "nanoid";
var viteLogger = createLogger();
function log(message, source = "express") {
  const formattedTime = (/* @__PURE__ */ new Date()).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true
  });
  console.log(`${formattedTime} [${source}] ${message}`);
}
async function setupVite(app2, server) {
  const serverOptions = {
    middlewareMode: true,
    hmr: { server },
    allowedHosts: true
  };
  const vite = await createViteServer({
    ...vite_config_default,
    configFile: false,
    customLogger: {
      ...viteLogger,
      error: (msg, options) => {
        viteLogger.error(msg, options);
        process.exit(1);
      }
    },
    server: serverOptions,
    appType: "custom"
  });
  app2.use(vite.middlewares);
  app2.use("*", async (req, res, next) => {
    const url = req.originalUrl;
    try {
      const clientTemplate = path2.resolve(
        import.meta.dirname,
        "..",
        "client",
        "index.html"
      );
      let template = await fs.promises.readFile(clientTemplate, "utf-8");
      template = template.replace(
        `src="/src/main.tsx"`,
        `src="/src/main.tsx?v=${nanoid()}"`
      );
      const page = await vite.transformIndexHtml(url, template);
      res.status(200).set({ "Content-Type": "text/html" }).end(page);
    } catch (e) {
      vite.ssrFixStacktrace(e);
      next(e);
    }
  });
}
function serveStatic(app2) {
  const distPath = path2.resolve(import.meta.dirname, "public");
  if (!fs.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`
    );
  }
  app2.use(express.static(distPath));
  app2.use("*", (_req, res) => {
    res.sendFile(path2.resolve(distPath, "index.html"));
  });
}

// server/index.ts
var app = express2();
app.use(express2.json());
app.use(express2.urlencoded({ extended: false }));
app.use((req, res, next) => {
  const start = Date.now();
  const path3 = req.path;
  let capturedJsonResponse = void 0;
  const originalResJson = res.json;
  res.json = function(bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };
  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path3.startsWith("/api")) {
      let logLine = `${req.method} ${path3} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }
      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "\u2026";
      }
      log(logLine);
    }
  });
  next();
});
(async () => {
  const server = await registerRoutes(app);
  app.use((err, _req, res, _next) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";
    res.status(status).json({ message });
    throw err;
  });
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }
  const port = parseInt(process.env.PORT || "5000", 10);
  server.listen({
    port,
    host: "0.0.0.0",
    reusePort: true
  }, () => {
    log(`serving on port ${port}`);
  });
})();
