type LogLevel = "debug" | "info" | "warn" | "error";

interface LogMessage {
  level: LogLevel;
  service: string;
  message: string;
  timestamp: string;
  data?: any;
}

class Logger {
  private static formatMessage(msg: LogMessage): string {
    const dataStr = msg.data ? `\n${JSON.stringify(msg.data, null, 2)}` : "";
    return `[${msg.timestamp}] ${msg.level.toUpperCase()} [${msg.service}] ${msg.message}${dataStr}`;
  }

  private static log(
    level: LogLevel,
    service: string,
    message: string,
    data?: any,
  ) {
    const logMsg: LogMessage = {
      level,
      service,
      message,
      timestamp: new Date().toISOString(),
      data,
    };

    console.log(Logger.formatMessage(logMsg));
  }

  public static debug(service: string, message: string, data?: any) {
    Logger.log("debug", service, message, data);
  }

  public static info(service: string, message: string, data?: any) {
    Logger.log("info", service, message, data);
  }

  public static warn(service: string, message: string, data?: any) {
    Logger.log("warn", service, message, data);
  }

  public static error(service: string, message: string, data?: any) {
    Logger.log("error", service, message, data);
  }
}

export default Logger;
