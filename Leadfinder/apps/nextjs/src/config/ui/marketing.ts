import type { Locale } from "~/config/i18n-config";
import { getDictionary } from "~/lib/get-dictionary";
import type { MarketingConfig } from "~/types";

export const getMarketingConfig = async ({
  params: { lang },
}: {
  params: {
    lang: Locale;
  };
}): Promise<MarketingConfig> => {
  const dict = await getDictionary(lang);
  return {
    mainNav: [
      {
        title: dict.marketing.main_nav_features,
        href: `/#features`,
      },
      {
        title: dict.marketing.main_nav_email_finder,
        href: `/email-finder`,
      },
      {
        title: dict.marketing.main_nav_single_verify,
        href: `/single-verify`,
      },
      {
        title: dict.marketing.main_nav_bulk_verify,
        href: `/bulk-verify`,
      },
      {
        title: dict.marketing.main_nav_bulk_finder,
        href: `/bulk-finder`,
      },
      {
        title: dict.marketing.main_nav_pricing,
        href: `/pricing`,
      },
      {
        title: dict.marketing.main_nav_blog,
        href: `/blog`,
      },
    ],
  };
};
