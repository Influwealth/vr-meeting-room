using UnityEngine;

public class LangRouterClient : MonoBehaviour
{
    private string currentLang = "en";

    public string GetLang()
    {
        return currentLang;
    }

    public void SetLang(string lang)
    {
        currentLang = string.IsNullOrEmpty(lang) ? "en" : lang;
        Debug.Log("Language changed (placeholder): " + currentLang);
    }
}

