import { z } from "zod";

export const createRunSchema = z.object({
  name: z.string().trim().min(3, "Enter a run name of at least 3 characters."),
  modelId: z.string().min(1, "Select a model."),
  suite_id: z.string().min(1, "Select a test suite."),
  temperature: z.coerce.number().min(0, "Minimum is 0.").max(2, "Maximum is 2."),
  max_tokens: z.coerce.number().int().min(16, "Minimum is 16.").max(8192, "Maximum is 8192."),
  timeout_seconds: z.coerce.number().int().min(5, "Minimum is 5.").max(600, "Maximum is 600."),
});

export type CreateRunForm = z.infer<typeof createRunSchema>;
