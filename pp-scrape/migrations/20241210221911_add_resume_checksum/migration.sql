/*
  Warnings:

  - You are about to drop the `processed_job_links` table. If the table is not empty, all the data it contains will be lost.

*/
-- AlterTable
ALTER TABLE "roles" ADD COLUMN "resume_checksum" TEXT;

-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "processed_job_links";
PRAGMA foreign_keys=on;

-- CreateIndex
CREATE INDEX "roles_link_idx" ON "roles"("link");

-- CreateIndex
CREATE INDEX "roles_resume_checksum_idx" ON "roles"("resume_checksum");
