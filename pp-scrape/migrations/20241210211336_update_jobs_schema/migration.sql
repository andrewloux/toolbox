-- CreateTable
CREATE TABLE "companies" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "website" TEXT,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "roles" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "company_id" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "link" TEXT NOT NULL,
    "location" TEXT,
    "pay_range" TEXT,
    "similarity_score" REAL NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'new',
    "disliked" BOOLEAN NOT NULL DEFAULT false,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "section_scores" TEXT,
    "analysis_json" TEXT,
    CONSTRAINT "roles_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "companies" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "resume_cache" (
    "fileChecksum" TEXT NOT NULL PRIMARY KEY,
    "processedText" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "processed_job_links" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "resumeChecksum" TEXT NOT NULL,
    "jobLink" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE UNIQUE INDEX "companies_name_website_key" ON "companies"("name", "website");

-- CreateIndex
CREATE UNIQUE INDEX "processed_job_links_resumeChecksum_jobLink_key" ON "processed_job_links"("resumeChecksum", "jobLink");
