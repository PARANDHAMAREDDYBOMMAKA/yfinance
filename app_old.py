from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import yfinance as yf
from datetime import datetime
import traceback
import requests

app = Flask(__name__)
CORS(app)

# Indian market stocks (NSE) - Only for default display
DEFAULT_SYMBOLS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS', 'LT.NS'
]

# Function to search stocks dynamically using Yahoo Finance API
def search_yahoo_finance(query):
    """Search for Indian stocks using Yahoo Finance API"""
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            'q': query,
            'quotesCount': 15,
            'newsCount': 0,
            'enableFuzzyQuery': False,
            'quotesQueryId': 'tss_match_phrase_query',
            'region': 'IN',
            'lang': 'en-IN'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            quotes = data.get('quotes', [])

            # Filter for Indian stocks (NSE and BSE)
            indian_stocks = []
            for quote in quotes:
                symbol = quote.get('symbol', '')
                # Only include NSE (.NS) and BSE (.BO) stocks
                if '.NS' in symbol or '.BO' in symbol:
                    indian_stocks.append({
                        'symbol': symbol,
                        'name': quote.get('longname') or quote.get('shortname', symbol)
                    })

            return indian_stocks

        return []

    except Exception as e:
        print(f"Error searching Yahoo Finance: {e}")
        return []

# Minimal fallback list (Nifty 50) for when API fails
FALLBACK_STOCKS = [
    {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries'},
    {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services'},
    {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank'},
    {'symbol': 'INFY.NS', 'name': 'Infosys'},
    {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank'},
    {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever'},
    {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel'},
    {'symbol': 'ITC.NS', 'name': 'ITC Limited'},
    {'symbol': 'SBIN.NS', 'name': 'State Bank of India'},
    {'symbol': 'LT.NS', 'name': 'Larsen & Toubro'},
    {'symbol': 'BAJFINANCE.NS', 'name': 'Bajaj Finance'},
    {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank'},
    {'symbol': 'HCLTECH.NS', 'name': 'HCL Technologies'},
    {'symbol': 'WIPRO.NS', 'name': 'Wipro'},
    {'symbol': 'ASIANPAINT.NS', 'name': 'Asian Paints'},
    {'symbol': 'MARUTI.NS', 'name': 'Maruti Suzuki'},
    {'symbol': 'TATAMOTORS.NS', 'name': 'Tata Motors'},
    {'symbol': 'TITAN.NS', 'name': 'Titan Company'},
    {'symbol': 'SUNPHARMA.NS', 'name': 'Sun Pharmaceutical'},
    {'symbol': 'ULTRACEMCO.NS', 'name': 'UltraTech Cement'},
    {'symbol': 'NESTLEIND.NS', 'name': 'Nestle India'},
    {'symbol': 'ONGC.NS', 'name': 'ONGC'},
    {'symbol': 'NTPC.NS', 'name': 'NTPC'},
    {'symbol': 'POWERGRID.NS', 'name': 'Power Grid Corporation'},
    {'symbol': 'AXISBANK.NS', 'name': 'Axis Bank'},
    {'symbol': 'M&M.NS', 'name': 'Mahindra & Mahindra'},
    {'symbol': 'TECHM.NS', 'name': 'Tech Mahindra'},
    {'symbol': 'TATASTEEL.NS', 'name': 'Tata Steel'},
    {'symbol': 'ADANIPORTS.NS', 'name': 'Adani Ports'},
    {'symbol': 'ADANIENT.NS', 'name': 'Adani Enterprises'},
    {'symbol': 'BAJAJFINSV.NS', 'name': 'Bajaj Finserv'},
    {'symbol': 'DIVISLAB.NS', 'name': 'Divi\'s Laboratories'},
    {'symbol': 'DRREDDY.NS', 'name': 'Dr. Reddy\'s Laboratories'},
    {'symbol': 'EICHERMOT.NS', 'name': 'Eicher Motors'},
    {'symbol': 'GRASIM.NS', 'name': 'Grasim Industries'},
    {'symbol': 'HEROMOTOCO.NS', 'name': 'Hero MotoCorp'},
    {'symbol': 'HINDALCO.NS', 'name': 'Hindalco Industries'},
    {'symbol': 'INDUSINDBK.NS', 'name': 'IndusInd Bank'},
    {'symbol': 'JSWSTEEL.NS', 'name': 'JSW Steel'},
    {'symbol': 'CIPLA.NS', 'name': 'Cipla'},
    {'symbol': 'BPCL.NS', 'name': 'Bharat Petroleum'},
    {'symbol': 'COALINDIA.NS', 'name': 'Coal India'},
    {'symbol': 'BRITANNIA.NS', 'name': 'Britannia Industries'},
    {'symbol': 'SHREECEM.NS', 'name': 'Shree Cement'},
    {'symbol': 'VEDL.NS', 'name': 'Vedanta'},
    {'symbol': 'APOLLOHOSP.NS', 'name': 'Apollo Hospitals'},
    {'symbol': 'TATACONSUM.NS', 'name': 'Tata Consumer Products'},
    {'symbol': 'ADANIGREEN.NS', 'name': 'Adani Green Energy'},
    {'symbol': 'SBILIFE.NS', 'name': 'SBI Life Insurance'},
    {'symbol': 'HDFCLIFE.NS', 'name': 'HDFC Life Insurance'},

    # Mid Cap Stocks
    {'symbol': 'BANKBARODA.NS', 'name': 'Bank of Baroda'},
    {'symbol': 'PNB.NS', 'name': 'Punjab National Bank'},
    {'symbol': 'CANBK.NS', 'name': 'Canara Bank'},
    {'symbol': 'UNIONBANK.NS', 'name': 'Union Bank of India'},
    {'symbol': 'IDBI.NS', 'name': 'IDBI Bank'},
    {'symbol': 'IOC.NS', 'name': 'Indian Oil Corporation'},
    {'symbol': 'GAIL.NS', 'name': 'GAIL India'},
    {'symbol': 'HINDPETRO.NS', 'name': 'Hindustan Petroleum'},
    {'symbol': 'SAIL.NS', 'name': 'Steel Authority of India'},
    {'symbol': 'NMDC.NS', 'name': 'NMDC'},
    {'symbol': 'BHEL.NS', 'name': 'Bharat Heavy Electricals'},
    {'symbol': 'BEL.NS', 'name': 'Bharat Electronics'},
    {'symbol': 'HAL.NS', 'name': 'Hindustan Aeronautics'},
    {'symbol': 'GODREJCP.NS', 'name': 'Godrej Consumer Products'},
    {'symbol': 'GODREJPROP.NS', 'name': 'Godrej Properties'},
    {'symbol': 'DLF.NS', 'name': 'DLF Limited'},
    {'symbol': 'OBEROIRLTY.NS', 'name': 'Oberoi Realty'},
    {'symbol': 'PRESTIGE.NS', 'name': 'Prestige Estates'},
    {'symbol': 'TRENT.NS', 'name': 'Trent Limited'},
    {'symbol': 'PIDILITIND.NS', 'name': 'Pidilite Industries'},
    {'symbol': 'BERGEPAINT.NS', 'name': 'Berger Paints'},
    {'symbol': 'CROMPTON.NS', 'name': 'Crompton Greaves'},
    {'symbol': 'HAVELLS.NS', 'name': 'Havells India'},
    {'symbol': 'VOLTAS.NS', 'name': 'Voltas'},
    {'symbol': 'CUMMINSIND.NS', 'name': 'Cummins India'},
    {'symbol': 'ABB.NS', 'name': 'ABB India'},
    {'symbol': 'SIEMENS.NS', 'name': 'Siemens'},
    {'symbol': 'BOSCHLTD.NS', 'name': 'Bosch'},
    {'symbol': 'MOTHERSON.NS', 'name': 'Samvardhana Motherson'},
    {'symbol': 'TVSMOTOR.NS', 'name': 'TVS Motor'},
    {'symbol': 'BAJAJ-AUTO.NS', 'name': 'Bajaj Auto'},
    {'symbol': 'ESCORTS.NS', 'name': 'Escorts Kubota'},
    {'symbol': 'ASHOKLEY.NS', 'name': 'Ashok Leyland'},
    {'symbol': 'TORNTPHARM.NS', 'name': 'Torrent Pharmaceuticals'},
    {'symbol': 'BIOCON.NS', 'name': 'Biocon'},
    {'symbol': 'LUPIN.NS', 'name': 'Lupin'},
    {'symbol': 'AUROPHARMA.NS', 'name': 'Aurobindo Pharma'},
    {'symbol': 'ALKEM.NS', 'name': 'Alkem Laboratories'},
    {'symbol': 'LALPATHLAB.NS', 'name': 'Dr Lal PathLabs'},
    {'symbol': 'DMART.NS', 'name': 'Avenue Supermarts (DMart)'},
    {'symbol': 'JUBLFOOD.NS', 'name': 'Jubilant FoodWorks'},
    {'symbol': 'IGL.NS', 'name': 'Indraprastha Gas'},
    {'symbol': 'MGL.NS', 'name': 'Mahanagar Gas'},
    {'symbol': 'PETRONET.NS', 'name': 'Petronet LNG'},
    {'symbol': 'ADANIPOWER.NS', 'name': 'Adani Power'},
    {'symbol': 'TATAPOWER.NS', 'name': 'Tata Power'},
    {'symbol': 'TORNTPOWER.NS', 'name': 'Torrent Power'},
    {'symbol': 'JSW.NS', 'name': 'JSW Energy'},

    # New Age Tech & Small Cap
    {'symbol': 'ZOMATO.NS', 'name': 'Zomato'},
    {'symbol': 'PAYTM.NS', 'name': 'Paytm'},
    {'symbol': 'NYKAA.NS', 'name': 'Nykaa'},
    {'symbol': 'POLICYBZR.NS', 'name': 'PB Fintech (Policybazaar)'},
    {'symbol': 'IRCTC.NS', 'name': 'IRCTC'},
    {'symbol': 'IRFC.NS', 'name': 'Indian Railway Finance'},
    {'symbol': 'RVNL.NS', 'name': 'Rail Vikas Nigam'},
    {'symbol': 'CONCOR.NS', 'name': 'Container Corporation'},
    {'symbol': 'LTTS.NS', 'name': 'L&T Technology Services'},
    {'symbol': 'LTIM.NS', 'name': 'LTIMindtree'},
    {'symbol': 'PERSISTENT.NS', 'name': 'Persistent Systems'},
    {'symbol': 'COFORGE.NS', 'name': 'Coforge'},
    {'symbol': 'MPHASIS.NS', 'name': 'Mphasis'},
    {'symbol': 'CYIENT.NS', 'name': 'Cyient'},
    {'symbol': 'DIXON.NS', 'name': 'Dixon Technologies'},
    {'symbol': 'AMBER.NS', 'name': 'Amber Enterprises'},
    {'symbol': 'TATAELXSI.NS', 'name': 'Tata Elxsi'},
    {'symbol': 'TATACHEM.NS', 'name': 'Tata Chemicals'},
    {'symbol': 'DEEPAKNTR.NS', 'name': 'Deepak Nitrite'},
    {'symbol': 'AARTI.NS', 'name': 'Aarti Industries'},
    {'symbol': 'SRF.NS', 'name': 'SRF Limited'},
    {'symbol': 'BALRAMCHIN.NS', 'name': 'Balrampur Chini'},
    {'symbol': 'DALBHARAT.NS', 'name': 'Dalmia Bharat'},
    {'symbol': 'JKCEMENT.NS', 'name': 'JK Cement'},
    {'symbol': 'RAMCOCEM.NS', 'name': 'Ramco Cements'},
    {'symbol': 'INDIACEM.NS', 'name': 'India Cements'},
    {'symbol': 'MSUMI.NS', 'name': 'Motherson Sumi Systems'},
    {'symbol': 'BALKRISIND.NS', 'name': 'Balkrishna Industries'},
    {'symbol': 'APOLLOTYRE.NS', 'name': 'Apollo Tyres'},
    {'symbol': 'CEAT.NS', 'name': 'CEAT'},
    {'symbol': 'MRF.NS', 'name': 'MRF'},
    {'symbol': 'PAGEIND.NS', 'name': 'Page Industries'},
    {'symbol': 'AFFLE.NS', 'name': 'Affle India'},
    {'symbol': 'ROUTE.NS', 'name': 'Route Mobile'},
    {'symbol': 'HFCL.NS', 'name': 'HFCL'},
    {'symbol': 'INDHOTEL.NS', 'name': 'Indian Hotels'},
    {'symbol': 'LEMONTREE.NS', 'name': 'Lemon Tree Hotels'},
    {'symbol': 'TIINDIA.NS', 'name': 'Tube Investments'},
    {'symbol': 'SONACOMS.NS', 'name': 'Sona BLW Precision Forgings'},
    {'symbol': 'ANGELONE.NS', 'name': 'Angel One'},
    {'symbol': 'MAZDOCK.NS', 'name': 'Mazagon Dock'},
    {'symbol': 'COCHINSHIP.NS', 'name': 'Cochin Shipyard'},
    {'symbol': 'GPPL.NS', 'name': 'Gujarat Pipavav Port'},
    {'symbol': 'ADANIGAS.NS', 'name': 'Adani Total Gas'},
    {'symbol': 'ATGL.NS', 'name': 'Adani Total Gas'},

    # More Mid & Small Cap
    {'symbol': 'IDEA.NS', 'name': 'Vodafone Idea'},
    {'symbol': 'YESBANK.NS', 'name': 'Yes Bank'},
    {'symbol': 'FEDERALBNK.NS', 'name': 'Federal Bank'},
    {'symbol': 'IDFCFIRSTB.NS', 'name': 'IDFC First Bank'},
    {'symbol': 'BANDHANBNK.NS', 'name': 'Bandhan Bank'},
    {'symbol': 'RBLBANK.NS', 'name': 'RBL Bank'},
    {'symbol': 'CHOLAFIN.NS', 'name': 'Cholamandalam Investment'},
    {'symbol': 'SHRIRAMFIN.NS', 'name': 'Shriram Finance'},
    {'symbol': 'MUTHOOTFIN.NS', 'name': 'Muthoot Finance'},
    {'symbol': 'LICHSGFIN.NS', 'name': 'LIC Housing Finance'},
    {'symbol': 'PFC.NS', 'name': 'Power Finance Corporation'},
    {'symbol': 'RECLTD.NS', 'name': 'REC Limited'},
    {'symbol': 'HUDCO.NS', 'name': 'HUDCO'},
    {'symbol': 'NIACL.NS', 'name': 'New India Assurance'},
    {'symbol': 'GICRE.NS', 'name': 'GIC Re'},
    {'symbol': 'STARHEALTH.NS', 'name': 'Star Health Insurance'},
    {'symbol': 'GODIGIT.NS', 'name': 'Go Digit Insurance'},

    # IT & Tech Services
    {'symbol': 'INFOEDGE.NS', 'name': 'Info Edge (Naukri)'},
    {'symbol': 'JUSTDIAL.NS', 'name': 'Just Dial'},
    {'symbol': 'MINDTREE.NS', 'name': 'Mindtree'},
    {'symbol': 'KPITTECH.NS', 'name': 'KPIT Technologies'},
    {'symbol': 'HAPPSTMNDS.NS', 'name': 'Happiest Minds'},
    {'symbol': 'BIRLASOFT.NS', 'name': 'Birlasoft'},
    {'symbol': 'MASTEK.NS', 'name': 'Mastek'},
    {'symbol': 'TATATECH.NS', 'name': 'Tata Technologies'},
    {'symbol': 'NETWEB.NS', 'name': 'Netweb Technologies'},

    # Recently Listed & New Age
    {'symbol': 'TATATECH.NS', 'name': 'Tata Technologies'},
    {'symbol': 'IDEAFORGE.NS', 'name': 'IdeaForge Technology'},
    {'symbol': 'JYOTHYLAB.NS', 'name': 'Jyothy Labs'},
    {'symbol': 'POONAWALLA.NS', 'name': 'Poonawalla Fincorp'},
    {'symbol': 'KAYNES.NS', 'name': 'Kaynes Technology'},
    {'symbol': 'BIKAJI.NS', 'name': 'Bikaji Foods'},
    {'symbol': 'MAPMYINDIA.NS', 'name': 'MapMyIndia'},
    {'symbol': 'EASEMYTRIP.NS', 'name': 'EaseMyTrip'},
    {'symbol': 'CARTRADE.NS', 'name': 'CarTrade Tech'},
    {'symbol': 'LATENTVIEW.NS', 'name': 'LatentView Analytics'},
    {'symbol': 'SAPPHIRE.NS', 'name': 'Sapphire Foods'},
    {'symbol': 'MEDPLUS.NS', 'name': 'MedPlus Health'},
    {'symbol': 'RAINBOW.NS', 'name': 'Rainbow Childrens Hospital'},
    {'symbol': 'Krishna.NS', 'name': 'Krishna Institute of Medical Sciences'},
    {'symbol': 'YATRA.NS', 'name': 'Yatra Online'},
    {'symbol': 'METROPOLIS.NS', 'name': 'Metropolis Healthcare'},
    {'symbol': 'THYROCARE.NS', 'name': 'Thyrocare Technologies'},

    # Pharma & Healthcare
    {'symbol': 'GRANULES.NS', 'name': 'Granules India'},
    {'symbol': 'GLENMARK.NS', 'name': 'Glenmark Pharmaceuticals'},
    {'symbol': 'NATCOPHARM.NS', 'name': 'Natco Pharma'},
    {'symbol': 'AJANTPHARM.NS', 'name': 'Ajanta Pharma'},
    {'symbol': 'IPCALAB.NS', 'name': 'IPCA Laboratories'},
    {'symbol': 'LAURUSLABS.NS', 'name': 'Laurus Labs'},
    {'symbol': 'SUVEN.NS', 'name': 'Suven Pharmaceuticals'},
    {'symbol': 'SYNGENE.NS', 'name': 'Syngene International'},
    {'symbol': 'STRIDES.NS', 'name': 'Strides Pharma'},
    {'symbol': 'SOLARA.NS', 'name': 'Solara Active Pharma'},

    # Auto & Auto Components
    {'symbol': 'EXIDEIND.NS', 'name': 'Exide Industries'},
    {'symbol': 'AMARA.NS', 'name': 'Amara Raja Batteries'},
    {'symbol': 'FORCEMOT.NS', 'name': 'Force Motors'},
    {'symbol': 'MAHINDCIE.NS', 'name': 'Mahindra CIE Automotive'},
    {'symbol': 'ENDURANCE.NS', 'name': 'Endurance Technologies'},
    {'symbol': 'SCHAEFFLER.NS', 'name': 'Schaeffler India'},
    {'symbol': 'SUPRAJIT.NS', 'name': 'Suprajit Engineering'},
    {'symbol': 'SUNDRMFAST.NS', 'name': 'Sundaram Fasteners'},
    {'symbol': 'BODALCHEM.NS', 'name': 'Bodal Chemicals'},
    {'symbol': 'FIEM.NS', 'name': 'Fiem Industries'},

    # Textiles & Apparel
    {'symbol': 'AARVEE.NS', 'name': 'Aarvee Denims'},
    {'symbol': 'ARVIND.NS', 'name': 'Arvind Limited'},
    {'symbol': 'RAYMOND.NS', 'name': 'Raymond'},
    {'symbol': 'GOKEX.NS', 'name': 'Gokal Das Exports'},
    {'symbol': 'TRIDENT.NS', 'name': 'Trident'},
    {'symbol': 'WELSPUNIND.NS', 'name': 'Welspun India'},
    {'symbol': 'SKNL.NS', 'name': 'SKNL'},

    # Metals & Steel
    {'symbol': 'JINDALSTEL.NS', 'name': 'Jindal Steel & Power'},
    {'symbol': 'JSWENERGY.NS', 'name': 'JSW Energy'},
    {'symbol': 'SAIL.NS', 'name': 'SAIL'},
    {'symbol': 'RATNAMANI.NS', 'name': 'Ratnamani Metals'},
    {'symbol': 'KALYANKJIL.NS', 'name': 'Kalyan Jewellers'},
    {'symbol': 'TITAN.NS', 'name': 'Titan Company'},

    # Chemicals & Fertilizers
    {'symbol': 'PIIND.NS', 'name': 'PI Industries'},
    {'symbol': 'SUMICHEM.NS', 'name': 'Sumitomo Chemical'},
    {'symbol': 'UPL.NS', 'name': 'UPL'},
    {'symbol': 'COROMANDEL.NS', 'name': 'Coromandel International'},
    {'symbol': 'GNFC.NS', 'name': 'Gujarat Narmada Valley Fertilizers'},
    {'symbol': 'CHAMBLFERT.NS', 'name': 'Chambal Fertilizers'},
    {'symbol': 'FACT.NS', 'name': 'FACT'},
    {'symbol': 'NFL.NS', 'name': 'National Fertilizers'},
    {'symbol': 'ATUL.NS', 'name': 'Atul Ltd'},
    {'symbol': 'NAVNETEDUL.NS', 'name': 'Navneet Education'},
    {'symbol': 'FINEORG.NS', 'name': 'Fine Organic Industries'},
    {'symbol': 'CLEAN.NS', 'name': 'Clean Science'},
    {'symbol': 'ALKYLAMINE.NS', 'name': 'Alkyl Amines Chemicals'},
    {'symbol': 'TATACHEMICAL.NS', 'name': 'Tata Chemicals'},
    {'symbol': 'NOCIL.NS', 'name': 'NOCIL'},

    # Infrastructure & Construction
    {'symbol': 'NBCC.NS', 'name': 'NBCC India'},
    {'symbol': 'NXTDIGITAL.NS', 'name': 'NXT Digital'},
    {'symbol': 'KEC.NS', 'name': 'KEC International'},
    {'symbol': 'KALPATPOWR.NS', 'name': 'Kalpataru Power'},
    {'symbol': 'AJMERA.NS', 'name': 'Ajmera Realty'},
    {'symbol': 'PHOENIXLTD.NS', 'name': 'Phoenix Mills'},
    {'symbol': 'BRIGADE.NS', 'name': 'Brigade Enterprises'},
    {'symbol': 'SOBHA.NS', 'name': 'Sobha'},
    {'symbol': 'MAHLIFE.NS', 'name': 'Mahindra Lifespace'},
    {'symbol': 'SUNTECK.NS', 'name': 'Sunteck Realty'},

    # Food & Beverages
    {'symbol': 'VARUN.NS', 'name': 'Varun Beverages'},
    {'symbol': 'TATACONSUM.NS', 'name': 'Tata Consumer'},
    {'symbol': 'MARICO.NS', 'name': 'Marico'},
    {'symbol': 'DABUR.NS', 'name': 'Dabur India'},
    {'symbol': 'EMAMI.NS', 'name': 'Emami'},
    {'symbol': 'COLPAL.NS', 'name': 'Colgate Palmolive'},
    {'symbol': 'GILLETTE.NS', 'name': 'Gillette India'},
    {'symbol': 'VBL.NS', 'name': 'Varun Beverages'},
    {'symbol': 'TASTYBITE.NS', 'name': 'Tasty Bite Eatables'},
    {'symbol': 'HATSUN.NS', 'name': 'Hatsun Agro'},
    {'symbol': 'HERITGFOOD.NS', 'name': 'Heritage Foods'},
    {'symbol': 'PGHH.NS', 'name': 'Procter & Gamble Hygiene'},
    {'symbol': 'JUBLPHARMA.NS', 'name': 'Jubilant Pharmova'},
    {'symbol': 'VGUARD.NS', 'name': 'V-Guard Industries'},
    {'symbol': 'WHIRLPOOL.NS', 'name': 'Whirlpool India'},
    {'symbol': 'BLUESTARCO.NS', 'name': 'Blue Star'},

    # Media & Entertainment
    {'symbol': 'PVRINOX.NS', 'name': 'PVR Inox'},
    {'symbol': 'SAREGAMA.NS', 'name': 'Saregama India'},
    {'symbol': 'TV18BRDCST.NS', 'name': 'TV18 Broadcast'},
    {'symbol': 'NETWORK18.NS', 'name': 'Network18 Media'},
    {'symbol': 'DISHTV.NS', 'name': 'Dish TV'},
    {'symbol': 'SUNTV.NS', 'name': 'Sun TV Network'},
    {'symbol': 'ZEEL.NS', 'name': 'Zee Entertainment'},
    {'symbol': 'NAZARA.NS', 'name': 'Nazara Technologies'},

    # Logistics & Transport
    {'symbol': 'BLUEDART.NS', 'name': 'Blue Dart Express'},
    {'symbol': 'DELHIVERY.NS', 'name': 'Delhivery'},
    {'symbol': 'TCI.NS', 'name': 'Transport Corporation of India'},
    {'symbol': 'VRL.NS', 'name': 'VRL Logistics'},
    {'symbol': 'GATI.NS', 'name': 'Gati'},
    {'symbol': 'MAHLOG.NS', 'name': 'Mahindra Logistics'},
    {'symbol': 'SPICEJET.NS', 'name': 'SpiceJet'},
    {'symbol': 'INDIGO.NS', 'name': 'InterGlobe Aviation (IndiGo)'},

    # Renewable Energy & Green
    {'symbol': 'SUZLON.NS', 'name': 'Suzlon Energy'},
    {'symbol': 'WEBELSOLAR.NS', 'name': 'Websol Energy'},
    {'symbol': 'RPOWER.NS', 'name': 'Reliance Power'},
    {'symbol': 'JSWENERGY.NS', 'name': 'JSW Energy'},
    {'symbol': 'NHPC.NS', 'name': 'NHPC'},
    {'symbol': 'SJVN.NS', 'name': 'SJVN'},
    {'symbol': 'GUJALKALI.NS', 'name': 'Gujarat Alkalies'},

    # E-commerce & Digital
    {'symbol': 'FSL.NS', 'name': 'Firstsource Solutions'},
    {'symbol': 'INTELLECT.NS', 'name': 'Intellect Design Arena'},
    {'symbol': 'RAMCOCEM.NS', 'name': 'Ramco Cements'},
    {'symbol': 'DELTACORP.NS', 'name': 'Delta Corp'},

    # Defense & Aerospace
    {'symbol': 'GARFIBRES.NS', 'name': 'Garware Technical Fibres'},
    {'symbol': 'ASTRAZEN.NS', 'name': 'AstraZeneca Pharma'},
    {'symbol': 'GRSE.NS', 'name': 'Garden Reach Shipbuilders'},
    {'symbol': 'MIDHANI.NS', 'name': 'Mishra Dhatu Nigam'},

    # Agriculture & Agro
    {'symbol': 'KAVERIASEED.NS', 'name': 'Kaveri Seed'},
    {'symbol': 'BBTC.NS', 'name': 'Bombay Burmah Trading'},
    {'symbol': 'DHANUKA.NS', 'name': 'Dhanuka Agritech'},
    {'symbol': 'RALLIS.NS', 'name': 'Rallis India'},
    {'symbol': 'BASF.NS', 'name': 'BASF India'},

    # Specialty & Others
    {'symbol': 'FINPIPE.NS', 'name': 'Finolex Industries'},
    {'symbol': 'SUPERPIPES.NS', 'name': 'Super Pipes'},
    {'symbol': 'ASTRAL.NS', 'name': 'Astral'},
    {'symbol': 'IFBIND.NS', 'name': 'IFB Industries'},
    {'symbol': 'SYMPHONY.NS', 'name': 'Symphony'},
    {'symbol': 'ORIENTELEC.NS', 'name': 'Orient Electric'},
    {'symbol': 'POLYCAB.NS', 'name': 'Polycab India'},
    {'symbol': 'KEIIND.NS', 'name': 'KEI Industries'},
    {'symbol': 'EIDPARRY.NS', 'name': 'EID Parry'},
    {'symbol': 'PCJEWELLER.NS', 'name': 'PC Jeweller'},
    {'symbol': 'SENCO.NS', 'name': 'Senco Gold'},
    {'symbol': 'APLAPOLLO.NS', 'name': 'APL Apollo Tubes'},
    {'symbol': 'SKIPPER.NS', 'name': 'Skipper'},
    {'symbol': 'FINCABLES.NS', 'name': 'Finolex Cables'},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol.upper())

        info = ticker.info

        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', 0)

        change = current_price - previous_close if current_price and previous_close else 0
        change_percent = (change / previous_close * 100) if previous_close else 0

        data = {
            'symbol': symbol.upper(),
            'name': info.get('longName', symbol.upper()),
            'price': round(current_price, 2) if current_price else 0,
            'change': round(change, 2),
            'changePercent': round(change_percent, 2),
            'previousClose': round(previous_close, 2) if previous_close else 0,
            'open': round(info.get('open', 0), 2),
            'dayHigh': round(info.get('dayHigh', 0), 2),
            'dayLow': round(info.get('dayLow', 0), 2),
            'volume': info.get('volume', 0),
            'marketCap': info.get('marketCap', 0),
            'fiftyTwoWeekHigh': round(info.get('fiftyTwoWeekHigh', 0), 2),
            'fiftyTwoWeekLow': round(info.get('fiftyTwoWeekLow', 0), 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400

@app.route('/api/stocks/multiple')
def get_multiple_stocks():
    try:
        stocks_data = []

        for symbol in DEFAULT_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                previous_close = info.get('previousClose', 0)

                change = current_price - previous_close if current_price and previous_close else 0
                change_percent = (change / previous_close * 100) if previous_close else 0

                stocks_data.append({
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'price': round(current_price, 2) if current_price else 0,
                    'change': round(change, 2),
                    'changePercent': round(change_percent, 2)
                })
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue

        return jsonify({
            'stocks': stocks_data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400

@app.route('/api/history/<symbol>')
def get_stock_history(symbol):
    try:
        ticker = yf.Ticker(symbol.upper())

        hist = ticker.history(period='1d', interval='5m')

        if hist.empty:
            return jsonify({'error': 'No historical data available'}), 404

        history_data = []
        for index, row in hist.iterrows():
            history_data.append({
                'time': index.strftime('%H:%M'),
                'price': round(row['Close'], 2),
                'volume': int(row['Volume'])
            })

        return jsonify({
            'symbol': symbol.upper(),
            'history': history_data
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400

@app.route('/api/search/suggestions')
def search_suggestions():
    try:
        query = request.args.get('q', '').strip().upper()

        if not query:
            return jsonify({'suggestions': []})

        # Filter stocks based on query with prioritization
        exact_matches = []
        starts_with_matches = []
        contains_matches = []

        for stock in INDIAN_STOCKS:
            symbol_upper = stock['symbol'].upper()
            name_upper = stock['name'].upper()

            # Remove .NS for symbol matching
            symbol_clean = symbol_upper.replace('.NS', '')

            # Exact match (highest priority)
            if symbol_clean == query or name_upper == query:
                exact_matches.append(stock)
            # Starts with match (medium priority)
            elif symbol_clean.startswith(query) or name_upper.startswith(query):
                starts_with_matches.append(stock)
            # Contains match (lowest priority)
            elif query in symbol_clean or query in name_upper:
                contains_matches.append(stock)

        # Combine all matches with priority order
        suggestions = exact_matches + starts_with_matches + contains_matches

        # Limit to 15 suggestions for better coverage
        suggestions = suggestions[:15]

        return jsonify({'suggestions': suggestions})

    except Exception as e:
        return jsonify({
            'error': str(e),
            'suggestions': []
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
