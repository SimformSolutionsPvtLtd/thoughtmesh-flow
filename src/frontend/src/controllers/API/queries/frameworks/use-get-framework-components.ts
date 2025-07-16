import { useQueryFunctionType } from "../../../../types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

export interface FrameworkComponent {
  id: string;
  name: string;
  display_name: string;
  description: string;
  category: string;
  framework: string;
  version: string;
  icon: string | null;
  inputs: Array<{
    name: string;
    display_name: string;
    type: string;
    required: boolean;
    description: string;
    default: any;
    options: string[] | null;
    min_value: number | null;
    max_value: number | null;
  }>;
  outputs: Array<{
    name: string;
    display_name: string;
    type: string;
    description: string;
  }>;
  config_schema: Record<string, any>;
  tags: string[];
  documentation_url: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface FrameworkComponentsResponse {
  components: FrameworkComponent[];
}

interface GetFrameworkComponentsParams {
  framework: string;
}

export const useGetFrameworkComponents: useQueryFunctionType<
  GetFrameworkComponentsParams,
  FrameworkComponentsResponse
> = (params, options) => {
  const { query } = UseRequestProcessor();

  async function getFrameworkComponentsFn(): Promise<FrameworkComponentsResponse> {
    const res = await api.get<FrameworkComponentsResponse>(
      `${getURL("FRAMEWORKS")}/${params?.framework}/components`
    );
    return res.data;
  }

  const queryResult = query(
    ["useGetFrameworkComponents", params?.framework],
    getFrameworkComponentsFn,
    {
      enabled: !!params?.framework,
      ...options,
    },
  );

  return queryResult;
};
