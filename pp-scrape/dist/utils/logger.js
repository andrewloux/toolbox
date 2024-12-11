"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
class Logger {
    static formatMessage(msg) {
        const dataStr = msg.data ? `\n${JSON.stringify(msg.data, null, 2)}` : "";
        return `[${msg.timestamp}] ${msg.level.toUpperCase()} [${msg.service}] ${msg.message}${dataStr}`;
    }
    static log(level, service, message, data) {
        const logMsg = {
            level,
            service,
            message,
            timestamp: new Date().toISOString(),
            data,
        };
        console.log(Logger.formatMessage(logMsg));
    }
    static debug(service, message, data) {
        Logger.log("debug", service, message, data);
    }
    static info(service, message, data) {
        Logger.log("info", service, message, data);
    }
    static warn(service, message, data) {
        Logger.log("warn", service, message, data);
    }
    static error(service, message, data) {
        Logger.log("error", service, message, data);
    }
}
exports.default = Logger;
