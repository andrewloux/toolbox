-- CreateTable
CREATE TABLE "processed_job_links" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "resumeChecksum" TEXT NOT NULL,
    "jobLink" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE UNIQUE INDEX "processed_job_links_resumeChecksum_jobLink_key" ON "processed_job_links"("resumeChecksum", "jobLink");
