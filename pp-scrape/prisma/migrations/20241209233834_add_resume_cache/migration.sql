-- CreateTable
CREATE TABLE "resume_cache" (
    "fileChecksum" TEXT NOT NULL PRIMARY KEY,
    "processedText" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
