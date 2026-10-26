import { useQuery } from "@tanstack/react-query";
import { listTestSuites } from "../../services/runsService";

export const useTestSuites = () => useQuery({ queryKey: ["test-suites"], queryFn: listTestSuites });
