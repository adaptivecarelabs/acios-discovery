from bs4 import BeautifulSoup, Tag

from acios_discovery.domain.discovery.models import RawDiscovery


class FinelibDetailMapper:


    def _field_value(
        self,
        soup: BeautifulSoup,
        heading: str,
    ) -> str | None:
        """
        Returns the text contained in the <p> immediately
        following a matching <h3>.
        """

        for title in soup.find_all("h3"):

            if not isinstance(title, Tag):
                continue

            if title.get_text(strip=True) != heading:
                continue

            value = title.find_next("p")

            if value is None:
                return None

            text = value.get_text(
                separator="\n",
                strip=True,
            )

            return text or None

        return None



    def extract_email(
        self,
        soup: BeautifulSoup,
    ) -> str | None:

        #
        # Standard mailto links
        #

        link = soup.find(
            "a",
            href=lambda href: (
                href is not None
                and href.startswith("mailto:")
            ),
        )

        if isinstance(link, Tag):

            href = link.get("href")

            if not isinstance(href, str):
                return None

            return (
                href.replace("mailto:", "")
                .strip()
            )

        #
        # Cloudflare Email Protection
        #

        for link in soup.find_all("a"):

            text = link.get_text(
                strip=True,
            )

            if "@" in text:
                return text

        return None


    def extract_website(
        self,
        soup: BeautifulSoup,
    ) -> str | None:

        container = soup.find(
            "div",
            class_="cmpny-lstng url",
        )

        if container is None:
            return None

        link = container.find(
            "a",
            href=True,
        )

        if link is None:
            return None

        href = link.get("href")

        if not isinstance(href, str):
            return None

        return href.strip()


    def extract_social_links(
        self,
        soup: BeautifulSoup,
    ) -> dict[str, str]:

        sections = soup.find_all(
            "div",
            class_="subb-bx MT-15",
        )

        for section in sections:

            links = section.find_all(
                "a",
                href=True,
            )

            if len(links) < 2:
                continue

            socials: dict[str, str] = {}

            for link in links:

                href = link.get("href")

                if not isinstance(href, str):
                    continue

                clean_href = href.strip()
                lower_href = clean_href.lower()

                if "facebook.com" in lower_href:
                    socials["facebook"] = clean_href

                elif "twitter.com" in href:
                    socials["twitter"] = clean_href

                elif "linkedin.com" in href:
                    socials["linkedin"] = clean_href

                elif "instagram.com" in href:
                    socials["instagram"] = clean_href

            if socials:
                return socials

        return {}


    def extract_year_founded(
        self,
        soup: BeautifulSoup,
    ) -> int | None:

        value = self._field_value(
            soup,
            "Year Founded",
        )

        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            return None


    def extract_employee_count(
        self,
        soup: BeautifulSoup,
    ) -> str | None:

        return self._field_value(
            soup,
            "Number of Employees",
        )


    def extract_business_locations(
        self,
        soup: BeautifulSoup,
    ) -> int | None:

        value = self._field_value(
            soup,
            "No. of Business Locations",
        )

        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            return None


    def extract_product_types(
        self,
        soup: BeautifulSoup,
    ) -> list[str]:

        value = self._field_value(
            soup,
            "Types of Product",
        )

        if value is None:
            return []

        products: list[str] = []

        for line in value.splitlines():

            text = line.strip()

            if not text:
                continue

            if text.startswith("All our products"):
                break

            products.append(text)

        return products


    def extract_payment_methods(
        self,
        soup: BeautifulSoup,
    ) -> list[str]:

        value = self._field_value(
            soup,
            "Kinds of Payments Accepted",
        )

        if value is None:
            return []

        return [
            payment.strip().replace("  ", " ")
            for payment in value.split(",")
            if payment.strip()
        ]


    def enrich(
        self,
        company: RawDiscovery,
        soup: BeautifulSoup,
    ) -> RawDiscovery:

        company.email = self.extract_email(soup)

        company.website = self.extract_website(soup)

        company.social_links = self.extract_social_links(soup)

        company.year_founded = self.extract_year_founded(soup)

        company.employee_count = self.extract_employee_count(soup)

        company.business_locations = (
            self.extract_business_locations(soup)
        )

        company.product_types = (
            self.extract_product_types(soup)
        )

        company.payment_methods = (
            self.extract_payment_methods(soup)
        )

        return company
