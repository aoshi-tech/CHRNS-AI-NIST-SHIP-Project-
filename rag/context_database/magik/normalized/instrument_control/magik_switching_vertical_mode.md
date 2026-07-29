---
doc_id: magik_switching_vertical_mode
source_id: MAGIK-009
title: Switching to Vertical Mode
instrument: MAGIK
workflow_stage: instrument_control
source_type: web_page
access_level: public
status: deprecated
owner: [contact details omitted]
last_reviewed: 2026-07-29
source_url_or_path: https://www.nist.gov/ncnr/magik-operational-notes/switching-vertical-mode
source_last_updated: 2026-05-27
citation_required: false
software: NICE
---

# Switching to Vertical Mode

> DEPRECATION NOTICE: This page is no longer being updated and the information may be out of date.

When operating in vertical mode, a different monochromator configuration is used.

The main monochromator (used in the default configuration for vertical-axis reflectometry) consists of 13 blades which rotate independently, while the adjustable monochromator has a vertical translation motion as well as rotation. The motor in NICE that allows you to switch between these is `monoTrans`, with the following mapping:

*   **vertical-rotation-axis mode (default):** `move monoTrans 0`
*   **horizontal-rotation-axis mode:** `move monoTrans 55` (units of mm)

<!-- Source: Switching to vertical mode | https://www.nist.gov/ncnr/magik-operational-notes/switching-vertical-mode. Removed site navigation, government website banners, footer, and metadata regarding Drupal/Cloudflare. -->
