export class LangRouterClient {
  private currentLang = "en";

  getLang() {
    return this.currentLang;
  }

  setLang(lang: string) {
    this.currentLang = lang && lang.trim().length ? lang : "en";
  }

  async localize(key: string, fallback: string) {
    void key;
    return fallback;
  }
}

