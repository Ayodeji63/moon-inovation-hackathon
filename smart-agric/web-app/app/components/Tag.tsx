import React from "react";

function Tag({ text, href }: { text: string; href: string }) {
  return (
    <a
      href={`#${href}`}
      className="text-[#131811] dark:text-white text-sm font-medium leading-normal"
    >
      {text}
    </a>
  );
}

export default Tag;
