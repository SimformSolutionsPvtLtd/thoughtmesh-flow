import {
  Disclosure,
  DisclosureContent,
  DisclosureTrigger,
} from "@/components/ui/disclosure";

import { ForwardedIconComponent } from "@/components/common/genericIconComponent";
import ShadTooltip from "@/components/common/shadTooltipComponent";
import { Button } from "@/components/ui/button";
import { SidebarHeader, SidebarTrigger } from "@/components/ui/sidebar";
import { FrameworkSwitcher } from "@/components/frameworkSwitcher";
import { memo } from "react";
import { SidebarHeaderComponentProps } from "../../types";
import FeatureToggles from "../featureTogglesComponent";
import { SearchInput } from "../searchInput";
import { SidebarFilterComponent } from "../sidebarFilterComponent";

const SidebarHeaderComponent = memo(
  ({
    showConfig,
    setShowConfig,
    showBeta,
    setShowBeta,
    showLegacy,
    setShowLegacy,
    searchInputRef,
    isInputFocused,
    search,
    handleInputFocus,
    handleInputBlur,
    handleInputChange,
    filterType,
    setFilterEdge,
    setFilterData,
    data,
  }: SidebarHeaderComponentProps) => {
    return (
      <SidebarHeader className="flex h-fit min-h-fit flex-col gap-2 p-4">
        <div className="flex items-center justify-between">
          <SidebarTrigger className="-ml-1" />
          <FeatureToggles 
            showBeta={showBeta}
            setShowBeta={setShowBeta}
            showLegacy={showLegacy}
            setShowLegacy={setShowLegacy}
          />
        </div>
        <div className="flex flex-col gap-2">
          <FrameworkSwitcher />
          <SearchInput 
            searchInputRef={searchInputRef}
            isInputFocused={isInputFocused}
            search={search}
            handleInputFocus={handleInputFocus}
            handleInputBlur={handleInputBlur}
            handleInputChange={handleInputChange}
          />
          <Disclosure>
            <DisclosureTrigger>
              <ShadTooltip content="Filter components">
                <Button
                  className="w-full justify-start"
                  variant="ghost"
                  size="sm"
                >
                  <ForwardedIconComponent
                    name="Settings"
                    className="mr-2 h-4 w-4 text-muted-foreground"
                  />
                  Filters
                </Button>
              </ShadTooltip>
            </DisclosureTrigger>
            <DisclosureContent>
              <SidebarFilterComponent 
                isInput={false}
                type={filterType?.type || ""}
                color={filterType?.color || ""}
                resetFilters={() => {
                  setFilterEdge([]);
                  setFilterData(data);
                }}
              />
            </DisclosureContent>
          </Disclosure>
        </div>
      </SidebarHeader>
    );
  },
);

SidebarHeaderComponent.displayName = "SidebarHeaderComponent";

export { SidebarHeaderComponent };
export default SidebarHeaderComponent;
