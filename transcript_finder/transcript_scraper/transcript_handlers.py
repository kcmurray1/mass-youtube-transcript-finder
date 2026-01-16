

def get_transcript_raw_text(transcript):
    """Return transcript as a single string"""
    return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])

def get_transcript_fast(self):
    # This JS script runs entirely inside the remote browser
    script = """
    return Array.from(document.querySelectorAll('ytd-transcript-segment-renderer'))
                .map(el => el.getAttribute('aria-label'))
                .join('\\n');
    """
    # One single network round-trip to the Hub
    full_transcript = self.driver.execute_script(script)
    return full_transcript