from typing import List, Iterator

from cigs.document import Document
from cigs.document.reader.youtube_reader import YouTubeReader
from cigs.knowledge.agent import AgentKnowledge


class YouTubeKnowledgeBase(AgentKnowledge):
    urls: List[str] = []
    reader: YouTubeReader = YouTubeReader()

    @property
    def document_lists(self) -> Iterator[List[Document]]:
        """Iterate over YouTube URLs and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
                Iterator[List[Document]]: Iterator yielding list of documents
        """

        for url in self.urls:
            yield self.reader.read(video_url=url)
