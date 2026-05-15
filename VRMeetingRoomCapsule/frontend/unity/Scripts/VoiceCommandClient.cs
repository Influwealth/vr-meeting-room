using UnityEngine;

public class VoiceCommandClient : MonoBehaviour
{
    public void OnVoiceCommand(string text)
    {
        Debug.Log("Voice command (placeholder): " + text);
    }
}

