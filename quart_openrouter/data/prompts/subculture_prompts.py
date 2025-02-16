"""
Contains subculture-specific prompts for different agent personalities. 

All the keys in subculture_prompts are the subcultures that are supported and must be in lowercase.
"""

SUBCULTURE_PROMPTS = {
    "crypto": """
    HODL: Originally a typo for "hold," it means to keep holding onto a cryptocurrency despite market fluctuations.
    FOMO: "Fear of Missing Out" — the anxiety that others are profiting while you're not.
    FUD: "Fear, Uncertainty, and Doubt" — negative information spread about a cryptocurrency, often to manipulate its price.
    DYOR: "Do Your Own Research" — a reminder to investigate before investing.
    BTFD: "Buy The F***ing Dip" — advice to purchase cryptocurrencies when prices drop.
    Whale: A person or entity holding a large amount of cryptocurrency, capable of influencing the market.
    Bagholder: Someone holding a cryptocurrency that has significantly dropped in value.
    Moon: When a cryptocurrency's price increases dramatically.
    Rekt: "Wrecked" — a significant financial loss due to poor trades or investments.
    Shilling: Promoting a cryptocurrency, often with the intent to boost its price.
    Altcoin: Any cryptocurrency that isn't Bitcoin.
    DeFi: Short for "Decentralized Finance," refers to financial applications built on blockchain.
    NFT: "Non-Fungible Token" — a unique digital asset representing ownership of a specific item or piece of content.
    Stablecoin: A cryptocurrency pegged to a stable asset, like USD.
    GM: "Good Morning" — a positive greeting used in the crypto community.
    WAGMI: "We're All Gonna Make It" — a statement of optimism and unity in the crypto community.
    NGMI: "Not Gonna Make It" — used to describe someone making poor decisions or lacking faith.
    Ser: A playful way of saying "sir," used in crypto forums.
    Lambo: Short for "Lamborghini," referring to significant wealth gained from crypto investments.
    Paper Hands: Someone who sells their crypto holdings quickly due to fear of losses.
    Diamond Hands: Someone who holds onto their crypto investments despite market volatility.
    Ape In: Investing in a cryptocurrency without conducting proper research.
    Shitcoin: A cryptocurrency with little or no value or utility.
    Tokenomics: The economic structure and incentives of a cryptocurrency.
    Rug Pull: A scam where developers abandon a project and take investors' funds
    Flippening: A hypothetical event where Ethereum surpasses Bitcoin in market cap.
    Yield Farming: Earning interest or rewards by staking or lending cryptocurrency in DeFi platforms.
    Staking: Locking up cryptocurrency to support blockchain operations and earn rewards.
    Airdrop: Free distribution of cryptocurrency to promote awareness or reward holders.
    """,
    "trading": """
    Pump and Dump: A scheme where the price is artificially inflated ("pumped") and then sold off ("dumped") for profit.
    ATH: "All-Time High" — the highest price ever reached
    ATL: "All-Time Low" — the lowest price ever reached
    Bullish: Expectation that the market will increase in value.
    Bearish: Expectation that the market will decrease in value.
    Long: Betting that the price will increase.
    Short: Betting that the price will decrease.
    Margin Call: When the broker demands additional funds to cover potential losses in leveraged trading.
    Liquidation: Forced closure of a leveraged position due to insufficient funds to cover losses.
    Stop-Loss: An order to sell a cryptocurrency once it reaches a certain price to limit losses.
    Crab Market: A sideways market where prices neither rise nor fall significantly.
    Dead Cat Bounce: A temporary recovery in price after a significant drop, followed by further decline.
    Dumping: Selling off large quantities of the traded assest, causing a price drop.
    Capitulation: Investors selling off their assets in panic during a significant market downturn.
    Bear Trap: A false market signal leading traders to believe prices will decline further.
    Bull Trap: A false market signal leading traders to believe prices will increase further
    Hedge: Investing to reduce risk or offset potential losses in volatile markets.
    Impermanent Loss: A temporary loss in value due to providing liquidity in a volatile market.
    Liquidity Pool: A pool of funds locked in a smart contract for decentralized trading.
    """,
    "4chan community": """
    PEPE: Refers to the Pepe the Frog meme, often associated with meme coins.
    Wen Lambo?: A playful question asking when ventures or investments will make one rich enough to buy a Lamborghini
    Fren: Playful way of saying "friend"
    Anons: Members of the crypto community, derived from "anonymous."
    McDonald's: Jokingly used to refer to a fallback career
    Giga-Chad: Refers to someone making bold and successful moves.
    """,
}
