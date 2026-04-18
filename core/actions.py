"""
Generic action base classes for browser automation.
Reusable by any site: subclass BaseElementAction (via BaseAtomicAction or BaseMolecularAction) or BasePageAction (page-level).

BaseElementAction is the shared ABC for runnable steps: page handle, accomplish() pipeline, and abstract
perform_action / verify_action. BaseAtomicAction and BaseMolecularAction are siblings under BaseElementAction.
"""
import logging
from abc import ABC, abstractmethod
from typing import Self

from playwright.async_api import Page

from .delays import DelayConfig
from .human_behavior import human_wait

logger = logging.getLogger(__name__)


class BaseElementAction(ABC):
    """Shared base for a single runnable automation step (atomic or molecular chain)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self._accomplished = False

    @property
    def accomplished(self) -> bool:
        return self._accomplished

    @abstractmethod
    async def perform_action(self) -> None:
        pass

    @abstractmethod
    async def verify_action(self) -> bool:
        pass

    async def accomplish(self) -> Self:
        """Run perform_action then verify_action; set _accomplished. Logs and sets False on failure."""
        try:
            await self.perform_action()
            self._accomplished = await self.verify_action()
        except Exception as e:
            logger.exception("%s Failed: %s", self.__class__.__name__, e)
            self._accomplished = False
        return self


class BaseAtomicAction(BaseElementAction):
    """One logical browser step. Subclass and implement perform_action() and verify_action()."""


class BaseMolecularAction(BaseElementAction):
    """Runs a chain of BaseAtomicAction steps with delay between them. Set chain_of_actions in subclass."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.chain_of_actions: list[BaseAtomicAction] = []

    async def execute_chain_of_actions(
        self,
        delay_between: DelayConfig = DelayConfig(min_ms=500, max_ms=1000),
    ) -> bool:
        """Run each action's accomplish(), then human_wait between. Returns False on first failure or empty chain."""
        if not self.chain_of_actions:
            logger.warning(
                "%s: chain_of_actions is empty; refusing to report success",
                self.__class__.__name__,
            )
            return False
        for action in self.chain_of_actions:
            logger.debug("Executing action: %s", action.__class__.__name__)
            action = await action.accomplish()
            if not action.accomplished:
                logger.error("Action %s failed", action.__class__.__name__)
                return False
            else:
                logger.info("Action %s succeeded", action.__class__.__name__)
            await human_wait(self.page, config=delay_between)
        return True

    async def perform_action(self) -> None:
        self._accomplished = await self.execute_chain_of_actions()

    async def verify_action(self) -> bool:
        return self._accomplished


class BasePageAction(ABC):
    """Abstract page-level orchestrator. Subclass must provide is_valid_page and wait_for_page_to_load (often via PageUtility before BasePageAction in MRO)."""

    def __init__(self, page: Page) -> None:
        self.page = page

    @abstractmethod
    def is_valid_page(self) -> bool:
        pass

    @abstractmethod
    async def wait_for_page_to_load(self) -> None:
        pass
