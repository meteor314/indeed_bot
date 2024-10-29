import { app, BrowserWindow, session } from "electron";
import path from "path";
import { buildIndeedURL } from "./utils/urlBuilder";
import  config  from "./config/config";

let mainWindow: BrowserWindow | null;

const createWindow = (): void => {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true, 
      contextIsolation: false, 
    },
  });

  const url = buildIndeedURL({
    job_title: config.job_title,
    location: config.location,
    contract: config.contract,
    region: config.region,
  });

  console.log("Loading URL:", url);

  mainWindow.loadURL(url);

  session.defaultSession.cookies
    .get({})
    .then((cookies) => {
      const PPID = cookies.find((cookie) => cookie.name === "PPID")?.value;
      if (!PPID) {
        console.log("PPID not found, please login first and relaunch the app");
      } else {
        console.log("PPID found, we can continue");
      }
    })
    .catch((error) => {
      console.error("Error getting cookies:", error);
    });
};

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
