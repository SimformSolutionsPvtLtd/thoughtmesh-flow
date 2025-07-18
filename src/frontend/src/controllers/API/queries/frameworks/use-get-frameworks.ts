import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

export interface FrameworksResponse {
  frameworks: string[];
}

export const useGetFrameworks: useQueryFunctionType<
  undefined,
  FrameworksResponse
> = (options) => {
  const { query } = UseRequestProcessor();

  const getFrameworksFn = async (): Promise<FrameworksResponse> => {
    try {
      const response = await api.get<FrameworksResponse>(`${getURL("FRAMEWORKS")}`);
      return response?.data;
    } catch (error) {
      console.error("[Frameworks] Error fetching frameworks:", error);
      throw error;
    }
  };

  const queryResult = query(
    ["useGetFrameworks"],
    () => getFrameworksFn(),
    {
      refetchOnWindowFocus: false,
      ...options,
    },
  );

  return queryResult;
};
