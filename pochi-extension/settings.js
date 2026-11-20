async function setup() {
  const settings = await chrome.storage.local.get({enabled: true, reminders: false});
  for (const key of Object.keys(settings)) {
    const field = document.getElementById(key);
    field.checked = settings[key];
    field.disabled = false;
    field.addEventListener('change', () => chrome.storage.local.set({[key]: field.checked}));
  }
}
setup();
