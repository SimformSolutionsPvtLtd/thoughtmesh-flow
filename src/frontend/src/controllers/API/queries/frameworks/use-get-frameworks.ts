import { useQueryFunctionType } from "../../../../types/api";
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

  async function getFrameworksFn(): Promise<FrameworksResponse> {
    const res = await api.get<FrameworksResponse>(`${getURL("FRAMEWORKS")}`);
    return res.data;
  }

  const queryResult = query(
    ["useGetFrameworks"],
    getFrameworksFn,
    options,
  );

  return queryResult;
};
