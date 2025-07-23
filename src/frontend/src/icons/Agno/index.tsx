import React, { forwardRef } from "react";
import SvgAgno from "./Agno.svg?react";

export const AgnoIcon = forwardRef<
  SVGSVGElement,
  React.PropsWithChildren<{}>
>((props, ref) => {
  return <SvgAgno ref={ref} {...props} />;
});
