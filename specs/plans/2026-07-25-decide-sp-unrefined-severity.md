---
slug: decide-sp-unrefined-severity
title: Decide whether sp-unrefined should escalate to error
verification: per-section
---

# Decide whether sp-unrefined should escalate to error

## Overview

- none — only `## Problem` is filled; nothing else exists yet to connect.

## Problem

Open decision from the refine-and-execute-specs-flow plan — revisit the warning's severity once there is evidence about unrefined plans

_(v1 backlog task — tags: ['specs', 'validation'])_

`specs.py validate` emits `sp-unrefined` at **warn** severity when a plan has a `tasks.md` and no
recorded refinement, deliberately leaving `applyReady` untouched — gating on refinement would break
every existing plan in every installed repo on upgrade, and the front's doctrine is that a sweep
never blocks on a judgment call. Whether the warning is strong enough is an open question, and the
plan's design says to revisit it "once there is evidence about how often plans reach apply
unrefined" — evidence, not argument. There is no trigger date; this stays parked until the
refinement record has enough history to read.
